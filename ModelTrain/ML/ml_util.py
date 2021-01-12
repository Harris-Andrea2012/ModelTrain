import pandas as pd

from ModelTrain.ML import linReg, lda



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
        model_linReg=linReg.LinRegModel(dataframe, params, projectName, projectId)
        return model_linReg
    if model =='LDA':

        model_lda = lda.lda(dataframe, params, projectName, projectId)
        return model_lda
    return None
    

   
   



