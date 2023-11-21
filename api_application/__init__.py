from flask import Flask,request,render_template,redirect,url_for, jsonify
from flask_restful import Api 
from flask_security import UserMixin, RoleMixin, Security, SQLAlchemyUserDatastore, hash_password, roles_required, auth_required, verify_password, login_user, logout_user, current_user, roles_accepted
from datetime import datetime, timedelta 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail,Message

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'f724f39fcae64ca2ba988bf09ee91c66'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']='Authentication-Token'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = 'f724f39fcae64ca2ba988bf09ee91c66'
app.config['SECURITY_REGISTERABLE'] = True
app.config['MAIL_SERVER']="smtp.googlemail.com"
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']="dcvarunv@gmail.com"
app.config['MAIL_USE_TLS']=True 
app.config['MAIL_PASSWORD']="pezxugesflslxthl"


mail = Mail(app)

db=SQLAlchemy(app)
migrate = Migrate(app, db)

api = Api(app, prefix="/api/v1")
from api_application import routes,models


    


# @app.route('/send_email/<email>',methods=['GET'])
# def send_email(email):
#     msg_title = 'Title'
#     sender = 'noreply@app.com'
#     msg = Message(msg_title, sender = sender, recipients = [email])
#     msg_body='This is a test email'
#     msg.body="" 
#     data = {
#         'app_name':"MAD2 - Grocerify",
#         "title":"grocerify",
#         "body":"This is a test email"
#     }
#     msg.html = render_template('email.html',data=data)
#     try:
#         mail.send(msg)
#         return "Email sent ..."
#     except Exception as e:
#         return(str(e))