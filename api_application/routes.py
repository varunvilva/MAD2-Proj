from api_application import api
from flask_restful import Resource, reqparse,output_json
from api_application import db
from api_application.models import *
from datetime import datetime, timedelta
from api_application.admin import *
from api_application.users import *
from .tasks import *

# @app.route('/index')
# def index():
#     return render_template("index.html")

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
    # return redirect(url_for('index'))
    return redirect("/login")


@app.route('/sayHello', methods=['GET', 'POST'])
def sayHello_view():
    res = sayHello.delay()
    return jsonify({"task_id":res.id}),200

# Code to get CSRF token:
# var script = document.createElement('script');
# script.src = 'https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js';
# document.head.appendChild(script);

# script.onload = function() {
#   axios.get('/login', { data: null, headers: { 'Content-Type': 'application/json' } })
#     .then(function (resp) {
#       var csrf_token = resp.data['response']['csrf_token'];
#       console.log('CSRF Token:', csrf_token);
#       // Use the CSRF token as needed
#     });
# };

