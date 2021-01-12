import pandas as pd

from ModelTrain.ML import linReg, lda



def df_to_html(df_file, convert_to_df= 'True', direction = 'head', numRows = 0, extra_class = None):
    
    
    class_string = 'table table-striped table-hover frame-style'
    if extra_class is not None:
        class_string += extra_class


   
    if convert_to_df == 'True':
        df = pd.read_csv(df_file)
    else:
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

def model_train(dataframe, model, params):
    if model == 'LinReg':
        model_linReg=linReg.LinRegModel(dataframe, params)
        return model_linReg
    if model =='LDA':

        model_lda = lda.lda(dataframe, params)
        return model_lda
    return None
    
def get_model_results(df, model_name, params):
    if model_name == 'LinReg':
        results = linReg.ytrue_ypredict(df, params)
        return results
    
    if model_name == 'LDA':
        results = df
        return results
   
    return None
   
   



