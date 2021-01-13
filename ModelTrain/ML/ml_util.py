import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape
from ModelTrain.ML import linReg, lda
from ModelTrain import db, app
from ModelTrain.models import Analyst, Project, Model
from flask import url_for, render_template
from flask_login import login_user, current_user
import os




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

def model_train(dataframe, model, params, projectName, projectId, analyst_id):
    if model == 'LinReg':
        model_result=linReg.LinRegModel(dataframe, params, projectName, projectId)  
    if model =='LDA':
        model_result = lda.lda(dataframe, params, projectName, projectId)

    

    project_model = Model(model_result['name'], model_result['score'], model_result['model_object'], 
                                    model_result['result'],model_result['project_id'])
    db.session.add(project_model)
    db.session.commit()
   


 



  
    

    
