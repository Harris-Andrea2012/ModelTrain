from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pickle
import os
import pandas as pd

import sys
sys.path.append('../ModelTrain')

from ModelTrain import app


def LinRegModel(df, y_col):
    print('STARTING LINEAR REGRESSION')
    y = df[y_col]
    x = df.drop([y_col], axis=1)

    x_train, x_test, y_train, y_test = train_test_split( x, y, test_size=0.2, random_state=100)

    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    score = r2_score(y_test, predictions)
   

    filename = 'linearModel.pkl'
    file_loc = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)

    with open(file_loc, 'wb') as file:
        pickle.dump(model, file)
    
    
    with open(file_loc, 'rb') as file:
        model_object = pickle.load(file)


    model = {
        'name': 'Linear Regression',
        'score': score,
        'model_object': model_object,
        'filename': filename
    }

    return model
    

def ytrue_ypredict(df, y_col):
    y = df[y_col]
    x = df.drop([y_col], axis=1)


    x_train, x_test, y_train, y_test = train_test_split(x, y , random_state=100, test_size=.2)

    model = LinearRegression()
    model.fit(x_train, y_train)

    ypredict =model.predict(x_test)

    true_pred_df = pd.DataFrame({'ytrue': y_test, 'ypredict': ypredict})


    return true_pred_df