from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pickle
import os
import pandas as pd

import sys
sys.path.append('../ModelTrain')





def LinRegModel(df, y_col, projectName, projectId):
    print('STARTING LINEAR REGRESSION')
    y = df[y_col]
    x = df.drop([y_col], axis=1)

    x_train, x_test, y_train, y_test = train_test_split( x, y, test_size=0.2, random_state=100)

    model_object = LinearRegression()
    model_object.fit(x_train, y_train)
    ypredict = model_object.predict(x_test)
    score = r2_score(y_test, ypredict)

    true_pred_df = pd.DataFrame({'ytrue': y_test, 'ypredict': ypredict})
   



    model = {
         'name': 'Linear Regression',
         'score': score,
         'model_object': model_object,
         'result': true_pred_df,
         'project_id': projectId,
         'project_name': projectName

        
     }

  
    return model
    

