from datetime import datetime
from ModelTrain import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Analyst.query.get(int(user_id))

class Analyst(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, unique=True, nullable=False)
    memberDate = db.Column(db.DateTime, nullable=False, default= datetime.utcnow)
    projects = db.relationship('Project', backref=db.backref('analyst', lazy=True), 
                                                    cascade = "all, delete, delete-orphan" )
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


    def __repr__(self):
        return f"Analyst: '{self.username}', '{self.email}'"



class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    lastAccessDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    rawData_name = db.Column(db.Text, nullable=False)
    rawData= db.Column(db.PickleType, nullable=False)
    procData_name = db.Column(db.Text)
    procData = db.Column(db.PickleType)
    analyst_id = db.Column(db.Integer, db.ForeignKey('analyst.id'), nullable=False)
    model = db.relationship('Model', backref= db.backref('project', lazy='subquery'), 
                                    cascade = "all,delete, delete-orphan" )

    def __init__(self, name, rawData_name,rawData, analyst_id):
        self.name=name
        self.rawData_name = rawData_name
        self.rawData = rawData
        self.analyst_id = analyst_id
        

    def __repr__(self):
        return f"Project: '{self.id}', '{self.name}', created by '{self.analyst_id}'"



class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Float, nullable=False)
    model_object = db.Column(db.PickleType, nullable=False)
    result_dataframe = db.Column(db.PickleType, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    def __init__(self, name, score, model_object, result_dataframe,project_id):
        self.name = name,
        self.score = score,
        self.model_object = model_object,
        self.result_dataframe = result_dataframe,
        self.project_id = project_id
        

    def __repr__(self):
        return f"Model: '{self.id}', '{self.name}', '{self.score}'"
