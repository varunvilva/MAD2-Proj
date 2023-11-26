from api_application import api
from flask_restful import Resource, reqparse, output_json
from api_application import db
from api_application.models import *
from datetime import datetime, timedelta
from api_application.admin import *
from api_application.users import *
from .tasks import *
from flask import send_file, make_response
from flask_excel import make_response_from_array
import pandas as pd
from celery.result import AsyncResult
from .auth import user_datastore


@app.route('/')
def landingPageUser():
    return "Hello World"


@app.route('/protected')
@roles_accepted('admin', 'user')
def landingPageAdmin():
    return render_template("user/landingPageuser.html")


@app.route('/profile')
@auth_required('token', 'session')
def profile():

    if current_user.is_authenticated:
        session_token = current_user.get_auth_token()
        return f'Welcome, {current_user.username}! Your session token is: {session_token}'
    else:
        return 'You are not logged in.'


@app.post('/user-login')
def user_login():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"message": "email not provided"}), 400

    user = user_datastore.find_user(email=email)

    if not user:
        return jsonify({"message": "User Not Found"}), 404
    
    if not user.active:
        return jsonify({"message": "User is not active"}), 400
    
    if verify_password(data.get("password"), user.password): 
        login_user(user)
        user.last_login_time = datetime.utcnow()
        db.session.commit()
        return jsonify({"token": user.get_auth_token(), "email": user.email, "role": user.roles[0].name, "message":"success"})
    else:
        return jsonify({"message": "FAILURE"}), 400


@app.route('/user-register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        try:
            print(user_datastore.find_user(email=email))
            if not user_datastore.find_user(email=email) and role == "user":
                print("User being added")
                user_datastore.create_user(username=username, email=email, password=hash_password(password), roles=[role])
            elif not user_datastore.find_user(email=email) and role == "manager":
                print("Manager being added")
                user_datastore.create_user(username=username, email=email, password=hash_password(password), roles=[role],active=False)
            else:
                print("User already exists or invalid role.")
            db.session.commit()
            return jsonify({"message": "success"}), 200
        except Exception as e:
            db.session.rollback()
            return f"An error occurred: {str(e)}"
    
@app.route('/user-activate/<int:user_id>', methods=['GET'])
@auth_required('token', 'session')
@roles_required('admin')
def manager_allowed(user_id):
    user = User.query.get(user_id)
    if user.roles[0].name == "user":
        return jsonify({"message": "User is a user and is already activated"}), 400
    if user:
        user.active = True
        db.session.commit()
        return jsonify({"message": "success"}), 200
    else:
        return jsonify({"message": "FAILURE"}), 404
        

@app.route('/logout', methods=['GET', 'POST'])
@auth_required('token', 'session')
def logout():
    current_user.last_loggout_time = datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect("/")


@app.route('/download-data/<int:user_id>', methods=['GET', 'POST'])
@auth_required('token', 'session')
@roles_accepted('user','manager')
def download_csv(user_id):
    task = create_csv.delay(user_id)
    return jsonify({"task_id": task.id}), 200


@app.get('/get-csv/<task_id>')
@auth_required('token', 'session')
@roles_accepted('user','manager')
def get_csv(task_id):
    res = AsyncResult(task_id)
    if res.ready():
        filename = res.result
        filename = filename.replace('/mnt/c', '')
        return send_file(filename, as_attachment=True)
    else:
        return {"message": "FAILURE"}, 404

@app.route('/get-all-managers',methods=['GET'])
@auth_required('token', 'session')
@roles_accepted('admin')
def get_all_managers():
    managers = User.query.filter_by(active=False).all()
    print(managers)
    l=[]
    for manager in managers:
        l.append({
            "id":manager.id,
            "username":manager.username,
            "email":manager.email,
            "active":manager.active
        })
    return l, 200