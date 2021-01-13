import pandas as pd

from ModelTrain.ML import linReg, lda
from ModelTrain import db, app
from ModelTrain.models import Analyst, Project, Model
from flask import url_for




def df_to_html(df_file, direction = 'head', numRows = 0, extra_class = None):
    
    
    class_string = 'table table-striped table-hover frame-style'
    if extra_class is not None:
        class_string += extra_class


   
    
    df = df_file
    
    max_rows = len(df.index)
    default = 20
    
    if max_rows > 50:
        max_rows = 50
    

    if direction == 'head':
      

        if numRows == 0 and max_rows > default:
            df = df.head(default)
            html_df = df.to_html(classes=class_string)
            return html_df
        if numRows == 0 and max_rows <= default:
            df = df.head(max_rows)
            html_df = df.to_html(classes=class_string)
            return html_df

        if numRows > 0 and numRows < max_rows:
            df = df.head(numRows)
            html_df = df.to_html(classes=class_string)
            return html_df

        if numRows > 0 and numRows >= max_rows:
            df = df.head(max_rows)
            html_df = df.to_html(classes=class_string)
            return html_df


    else:
        if numRows == 0 and max_rows > default:
            df = df.tail(default)
            html_df = df.to_html(classes=class_string)
            return html_df
        if numRows == 0 and max_rows <= default:
            df = df.tail(max_rows)
            html_df = df.to_html(classes=class_string)
            return html_df

        if numRows > 0 and numRows < max_rows:
            df = df.tail(numRows)
            html_df = df.to_html(classes=class_string)
            return html_df

        if numRows > 0 and numRows >= max_rows:
            df = df.tail(max_rows)
            html_df = df.to_html(classes=class_string)
            return html_df


def drop_nulls(dataframe):
    return dataframe.dropna(axis = 0, how= 'any', inplace = False)

def model_train(dataframe, model, params, projectName, projectId):
    if model == 'LinReg':
        model_result=linReg.LinRegModel(dataframe, params, projectName, projectId)  
    if model =='LDA':
        model_result = lda.lda(dataframe, params, projectName, projectId)

    

    project_model = Model(model_result['name'], model_result['score'], model_result['model_object'], 
                                    model_result['result'],model_result['project_id'])
    db.session.add(project_model)
    db.session.commit()

    
    # if model_result['name'] == 'Latent Dirichlet Allocation':
    #     modeled_df = df_to_html(model_result['result'], extra_class=' lda-result')
    #     model_extra = ''
    #     for (topic_id, topic) in model_result['model_object'].print_topics(num_topics=-1, num_words=5):
    #         line =  '<br>Topic Id: '+ str(topic_id)+ '<br>Topic: '+ str(topic) + '<br>'
    #         model_extra += line

    # if model_result['name'] == 'Linear Regression':
    #     modeled_df = df_to_html(model_result['result'])
    #     model_extra = None

    # model_return = {
    #     'name': model_result['name'],
    #     'score': model_result['score'],
    #     'projectName':model_result['projectName'],
    #     'dataframe': modeled_df,
    #     'model_extra': model_extra
    # }
    

    with app.test_request_context('/api'):
        project_id = model_result['project_id']
        url_for('projectPage',  project_id = project_id)


    

   
   



