from flask import Flask,request,render_template,redirect,url_for, jsonify
from flask_restful import Api 
from flask_security import UserMixin, RoleMixin, Security, SQLAlchemyUserDatastore, hash_password, roles_required, auth_required, verify_password, login_user, logout_user, current_user, roles_accepted
from datetime import datetime, timedelta 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'f724f39fcae64ca2ba988bf09ee91c66'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']='Authentication-Token'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = 'f724f39fcae64ca2ba988bf09ee91c66'


db=SQLAlchemy(app)
migrate = Migrate(app, db)

api = Api(app, prefix="/api/v1")
from api_application import routes,models
