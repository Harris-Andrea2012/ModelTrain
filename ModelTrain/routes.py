from flask import render_template, url_for, request, redirect, jsonify, make_response, session
from passlib.hash import pbkdf2_sha256
from ModelTrain import app, db, ALLOWED_EXTENSIONS
from ModelTrain.models import Analyst, Project, Model
import pickle
from ModelTrain.ML import linReg, lda
from flask_login import login_user, current_user, logout_user, login_required, confirm_login, fresh_login_required
import json
import os
from werkzeug.utils import secure_filename
from ModelTrain.ML.ml_util import df_to_html, drop_nulls, model_train, get_model_results
import pandas as pd
from datetime import datetime, timedelta
import traceback



@app.route('/', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = pbkdf2_sha256.hash(request.form['password'])

        if(Analyst.query.filter_by(email = email).first()== None):
            newAnalyst = Analyst(username, email, password)
            db.session.add(newAnalyst)
            db.session.commit()
            print('NEW USER CREATED')

            message = 'Account created successfully! You can now login.'
            style = 'success'
        else:
            message = 'A user already exists with that email! Please login or create a new account.'
            style = 'warning'
            print('USER ALREADY EXISTS')
        
        return render_template( 'signUp.html', message= message, style=style)

    return render_template('signUp.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Analyst.query.filter_by(email = email).first()

        if(user):
            if(pbkdf2_sha256.verify(password, user.password)):
                login_user(user, remember=True, duration=timedelta(days=1 ))
                confirm_login()
                return redirect(url_for('home'))
            invalid = 'Password is incorrect! Please try again.'
            return render_template('login.html', invalid=invalid)
        invalid = 'No account was found! Please create one.'
        return render_template('login.html', invalid=invalid)
    

    return render_template('login.html')


@app.route('/home')
@login_required
def home():
  
    
    projects = Project.query.filter_by(analyst_id = int(current_user.id)).all()
    if len(projects) >0:
        projects.sort(key = lambda x: x.lastAccessDate, reverse=True)
        recent_project = projects[0]
    else:
        recent_project = None
    

    return render_template('home.html', projects = projects, recent_project = recent_project)

@app.route('/home', methods=['POST'])
@login_required
@fresh_login_required
def editAccount():
    
    user = Analyst.query.get(int(current_user.id))
    for key in request.form.keys():
        if key == 'csrf_token':
            pass
        elif key == 'password':
            
            setattr(user, key, pbkdf2_sha256.hash(request.form[key]))
        else:
          
            setattr(user, key, request.form[key])

    db.session.commit()

    projects = current_user.projects
    if len(projects) >0:
        projects.sort(key = lambda x: x.lastAccessDate, reverse=True)
        recent_project = projects[0]
    else:
        recent_project = None

    return render_template('home.html', update = 'Account updated successfully!', projects = projects, recent_project = recent_project)


@app.route('/project/<int:project_id>')
@login_required
def projectPage(project_id):
    project = Project.query.get_or_404(project_id)
    if project != None:
        project.lastAccessDate = datetime.utcnow()
        db.session.commit()

        rawData = df_to_html(project.rawData, convert_to_df=False)

        proc_df = project.procData

        if proc_df is not None:
            
            procData = df_to_html(project.procData, convert_to_df=False)
        else:
            procData = None
        
        result_df = project.model[0].result_dataframe[0]
        model = project.model[0]
        
        if model.name =='Latent Dirichlet Allocation':
            result_df = df_to_html(result_df, convert_to_df=False, extra_class=' lda-result')
            model_object = model.model_object[0]
        if model.name == 'Linear Regression':
            result_df = df_to_html(result_df, convert_to_df=False)
            model_object = None
        
       
        
        data = {
            'project': project,
            'rawData':rawData,
            'procData': procData,
            'result_df': result_df,
            'model':model,
            'model_object': model_object
        }

       

       
    return render_template('project.html', data=data)

@app.route('/createProject')
@login_required
def createProject():
    
    return render_template('create.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


 
@app.route('/createProject/importData', methods=['POST'])
@login_required
def importData():
    upload_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    upload_size = os.listdir(upload_folder)
    print('UPLOAD_FOLDER SIZE ', upload_size)

    file = request.files['file']
    name = request.form['projectName']
    sep = request.form['seperator']

    if len(upload_size) > 1:

        old_file_name= os.listdir(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']))[1]
        old_file = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'] , old_file_name)
        os.remove(old_file)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        raw_df_path=os.path.join(app.root_path, app.config['UPLOAD_FOLDER'] ,filename)
        file.save(raw_df_path)

        raw_data = pd.read_csv(raw_df_path, sep = sep)

        #SAVE PROJECT TO DATABASE
       
        existing_project = Project.query.filter_by(name= name, analyst_id = current_user.id).first()
        

        if existing_project == None:
            new_project = Project(name, filename, raw_data, current_user.id)
            db.session.add(new_project)
            db.session.commit()
            print('NEW PROJECT ADDED TO DB')
            
            #CREATE DF TO DISPLAY TO PAGE
            table = df_to_html(df_file=raw_df_path)

            project = {
                'name': name,
                'filename': filename,
                'message': ' Dataset uploaded successfully! New Project Created!',
                'style': 'alert-success',
                'dataframe':table
            }
        
            res = make_response(jsonify(project), 200)
            print('NEW FILE ADDED')

            return res
        else:
            res = make_response(jsonify({'message': 'A project currently exists with that name! Please select a new name.',
                                                    'style': 'alert-danger'}))
            return res

    res = make_response(jsonify({'message': 'Invalid form type! Please upload a CSV file.',
                                                'style': 'alert-danger'}))
    
    
    return res


@app.route('/createProject/selectDfSize/<convert>', methods=['POST'])
@login_required 
def setDF_size(convert):
   
    
    numRows = request.form['numRows']
    direction = request.form['direction']

    if 'df_type' in request.form:
        df_type = request.form['df_type']
    else: 
        df_type = None
    
    if 'modelName' in request.form:
        modelName = request.form['modelName']
    else:
        modelName = None

    
    if convert == 'True':
        filename = request.form['filename']
        df_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
    else:
        project_name = request.form['projectName']
        
        project = Project.query.filter_by(name = project_name).first()

        if df_type == 'raw':
            df_path = project.rawData
        if df_type == 'proc':
            df_path = project.procData
        if df_type == 'res':
            df_path = project.model[0].result_dataframe[0]
    
    if modelName is not None and modelName == 'Latent Dirichlet Allocation' and df_type == 'res':
        dataframe = df_to_html(df_file=df_path, convert_to_df=convert, direction=direction, numRows=int(numRows), extra_class=' lda-result')
        
    else:
        dataframe = df_to_html(df_file=df_path, convert_to_df=convert,  direction=direction, numRows=int(numRows))


    data = {
        'dataframe': dataframe
     }

    res = make_response(jsonify(data), 200)
    return res



#function pre
@app.route('/createProject/model_and_run', methods=['POST'])
@login_required 
def create_run():
    preprocessMethod = request.form['preprocessMethod']
    modelType = request.form['modelType']



    if modelType == 'LinReg':
        params = request.form['params']
    if modelType =='LDA':

        
        #HANDLE STOP WORDS
        if request.form['extra_stop_words'] == '':
            extra_stop_words = []
        else:
            extra_stop_words = request.form['extra_stop_words'].split(', ')
           
    
        #HANDLE NUM TOPICS
        if request.form['num_topics'] == 'null':
            num_topics = None
        else:
            num_topics = int(request.form['num_topics'])
    
        #HANDLE ALPHA AND BETA
        if request.form['alpha'] == 'null':
            alpha = None
        else:
            alpha = float(request.form['alpha'])
    
        if request.form['beta'] == 'null':
            beta = None
        else:
            beta = float(request.form['beta'])
    

        params = {
            'extra_stop_words': extra_stop_words,
            'num_topics': num_topics, 
            'alpha': alpha,
            'beta': beta,
            'text_column': request.form['text_column']
        }

       
        
    #DF CREATION
    projectName = request.form['projectName']
    file = request.files['file']
    df_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], file.filename)
    df = pd.read_csv(df_path)
    
    found_project = Project.query.filter_by(analyst_id = current_user.id, name=projectName).first()
    if found_project != None:
        try:
            if preprocessMethod == 'yes':
                proc_dataframe=drop_nulls(df)
                try:
                    found_project.procData_name = projectName + '_processed'
                    found_project.procData = proc_dataframe
                    db.session.commit()

                    created=model_train(proc_dataframe, modelType, params)
                except Exception:
                    traceback.print_exc()
                    removeFiles()
                    print('FILE REMOVAL AFTER ERROR IN PREPROCESS BLOCK')
                    incomplete = Project.query.filter_by(name = projectName, analyst_id = current_user.id).first()
                    
                    if incomplete is not None:
                        db.session.delete(incomplete)
                        db.session.commit()
                        print('INCOMPLETE PROJECT REMOVED AFTER ERROR IN NONPREPROCESS BLOCK')
                   
                    err = 'ERROR OCCURRED IN PREPROCESS BLOCK'
                    res = make_response(jsonify({'message': err}), 400)
                    return res


            else:

                created = model_train(df, modelType, params)

            model_name = created['name']
            score = created['score']
            model_pkl = created['model_object']
            project_id = found_project.id


            if model_name == 'Linear Regression':
                modeled_df = get_model_results(df, modelType, params)
            if model_name == 'Latent Dirichlet Allocation':
                modeled_df = get_model_results(created['result'], modelType, params)
        
            project_model = Model(model_name, score, model_pkl, modeled_df, project_id)
            db.session.add(project_model)
            db.session.commit()

            model_csv_filename = projectName+ '_Model.csv'

            model_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], model_csv_filename)
            modeled_df.to_csv(model_path)

            if model_name == 'Latent Dirichlet Allocation':
                modeled_df = df_to_html(modeled_df, convert_to_df=False, extra_class=' lda-result')
                model_extra = ''
                for (topic_id, topic) in model_pkl.print_topics(num_topics=-1, num_words=5):
                    line =  '<br>Topic Id: '+ str(topic_id)+ '<br>Topic: '+ str(topic) + '<br>'
                    model_extra += line

            if model_name == 'Linear Regression':
                modeled_df = df_to_html(modeled_df, convert_to_df=False)
                model_extra = None

            model_return = {
                'name': model_name,
                'score': score,
                'model_filename': model_csv_filename,
                'dataframe': modeled_df,
                'model_extra': model_extra
            }

            res = make_response(jsonify(model_return), 200)
            return res
        except Exception:
            traceback.print_exc()
            removeFiles()
            print('FILE REMOVAL AFTER ERROR IN NONPREPROCESS BLOCK')

            incomplete = Project.query.filter_by(name = projectName, analyst_id = current_user.id).first()
            if incomplete is not None:
                db.session.delete(incomplete)
                db.session.commit()
                print('INCOMPLETE PROJECT REMOVED AFTER ERROR IN NONPREPROCESS BLOCK')
            err = 'ERROR OCCURRED IN CREATE_RUN GENERAL'
            res = make_response(jsonify({'message': err}), 400)
            return res
    
    
    else:
        print('ERROR IN OUTER LAYER: NO PROJECT FOUND BY NAME')
    
    

@app.route('/finishCreate')
@login_required
def finishCreate():
    removeFiles()
    checkComplete = Project.query.order_by(Project.lastAccessDate.desc()).first()
    if checkComplete is not None:
        if checkComplete.model == []:
            db.session.delete(checkComplete)
            db.session.commit()
            print('INCOMPLETE PROJECT DELETED')
        
    return make_response(jsonify({'message': 'Finished creating!'}), 200)

@app.route('/deleteProject/<int:project_id>')
@login_required
@fresh_login_required
def deleteProject(project_id):
   to_delete = Project.query.get_or_404(project_id)
   if to_delete != None:
        try:
            db.session.delete(to_delete)
            db.session.commit()
            print('PROJECT DELETED ')
            session['project_delete'] = 'Project deleted successfully!'
        except:
            print('PROJECT DELETE ERROR')
        
        projects = Project.query.filter_by(analyst_id = current_user.id).all()
        if len(projects) >0:
            projects.sort(key = lambda x: x.lastAccessDate, reverse=True)
            recent_project = projects[0]
        else:
            recent_project = None
        
        return render_template('home.html', update = 'Project deleted successfully!', projects = projects, recent_project = recent_project)
     

def removeFiles():
    uploads_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    try:
        for file in os.listdir(uploads_folder):
            print(file)
            if file == '.gitignore':
                pass
            else:
                file = os.path.join(uploads_folder, file)
                os.remove(file)
        print('DIRECTORY CLEARED')
    except:
        print('ERROR REMOVING USER SESSION FILES')

@app.route('/deleteAccount')
@login_required
@fresh_login_required 
def deleteAccount():
    acct = Analyst.query.get(int(current_user.id))
    if acct is not None:
        db.session.delete(acct)
        db.session.commit()
    return redirect(url_for('signUp'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    removeFiles()
    return redirect(url_for('signUp'))

