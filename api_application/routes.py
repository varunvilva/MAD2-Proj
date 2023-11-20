from api_application import api
from flask_restful import Resource, reqparse,output_json
from api_application import db
from api_application.models import *
from datetime import datetime, timedelta
from api_application.admin import *
from api_application.users import *
from .tasks import *
from flask import send_file,make_response
from flask_excel import make_response_from_array
import pandas as pd
from celery.result import AsyncResult


@app.route('/')
def landingPageUser():
    return "Hello World"

@app.route('/protected')
@roles_accepted('admin','user')
def landingPageAdmin():
    return render_template("user/landingPageuser.html")

@app.route('/profile')
@auth_required('token','session')
def profile():
    
    if current_user.is_authenticated:
        session_token = current_user.get_auth_token()
        return f'Welcome, {current_user.username}! Your session token is: {session_token}'
    else:
        return 'You are not logged in.'

@app.route('/admin-login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        user = app.Security.datastore.find_user(email=email)
        if user and verify_password(password, user.password):
            login_user(user)
            session_token = current_user.get_auth_token()
            return {"session-token":session_token},200
        else:
            return redirect('/admin-login')
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        y = app.Security.datastore.find_or_create_role(name='user', description='User')
        if not app.Security.datastore.find_user(username=username):
            app.Security.datastore.create_user(username=username,email=email, password=hash_password(password), roles=[y])

        db.session.commit()
        return redirect('/login')
    return render_template("register.html")


@app.route('/logout')
@auth_required()
def logout():
    current_user.active=1
    current_user.login_count = 0
    db.session.commit()
    logout_user()
    return redirect("/login")

@app.route('/download-data/<int:user_id>', methods=['GET', 'POST'])
@auth_required('token', 'session')
@roles_accepted('user')
def download_csv(user_id):
    task = create_csv.delay(user_id)
    return jsonify({"task_id":task.id}),200

@app.get('/get-csv/<task_id>')
@auth_required('token', 'session')
@roles_accepted('user')
def get_csv(task_id):
    res = AsyncResult(task_id)
    if res.ready():
        filename = res.result
        return send_file(filename,as_attachment=True)
    else:
        return {"message":"Task is not ready"},404





