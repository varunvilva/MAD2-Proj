from api_application import api
from flask_restful import Resource, reqparse,output_json
from api_application import db
from api_application.models import *
from datetime import datetime, timedelta
from api_application.admin import *
from api_application.users import *
from .tasks import *
from flask import send_file
from flask_excel import make_response_from_array
import pandas as pd

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


@app.route('/download-data/<int:user_id>', methods=['GET', 'POST'])
@auth_required('token', 'session')
@roles_accepted('user')
def download_csv(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    if not orders:
        return jsonify({"message": "No orders found for the user"}), 404
    user_data = []
    for order in orders:
        order_info = {
            "order_id": order.id,
            "placed_at": order.placed_at,
            "description": order.description,
            "items": []
        }

        for item in order.items:
            product_id = item.product_id
            item_info = {
                "product_id": item.product_id,
                "name": Product.query.filter_by(id=product_id).first().name,
                "manufacturer": Product.query.filter_by(id=product_id).first().manufacturer,
                "expiry": Product.query.filter_by(id=product_id).first().expiry,
                "rate_per_unit": Product.query.filter_by(id=product_id).first().rate_per_unit,
                "quantity_ordered": item.quantity,
                "total_price": item.total_price
            }
            order_info["items"].append(item_info)

        user_data.append(order_info)
    columns = ["order_id", "placed_at", "description", "product_id", "name", "manufacturer", "expiry", "rate_per_unit", "quantity_ordered", "total_price"]
    data = []
    data.append(columns)
    for record in user_data:
        for item in record["items"]:
            data.append([record["order_id"], str(record["placed_at"]), record["description"], item["product_id"], item["name"], item["manufacturer"], str(item["expiry"]), item["rate_per_unit"], item["quantity_ordered"], item["total_price"]])

    return make_response_from_array(data, "csv",file_name="export_data"),200


    # csv_content = []
    # for record in user_data:
    #     for key, value in record.items():
    #         if key != "items":
    #             csv_content.append(f"{key},{value}")
    #     for item in record["items"]:
    #         csv_content.append(",".join(str(value) for value in item.values()))

    # # Send CSV content as a file
    # csv_file = '\n'.join(csv_content)
    # response = send_file(
    #     csv_file,
    #     as_attachment=True,
    #     download_name=f'user_{user_id}_orders.csv',
    #     mimetype='text/csv'
    # )

    # return response

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

