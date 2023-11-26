from celery import shared_task
from celery.schedules import crontab
from .models import * 
from flask import jsonify
from flask_excel import make_response_from_array
from flask import send_file
import csv
from weasyprint import HTML
import os
from api_application.helperFunction import *

@shared_task(ignore_result=False)
def create_csv(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    print(orders)
    if not orders:
        return {"message": "No orders found for the user"}, 404
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

    # csv_file_path = "C:\\Programming\\MAD2_API\\test.csv"
    filename = "test.csv"
    base_dir = os.path.dirname(os.path.realpath(__file__))
    full_path = os.path.join(base_dir, filename)
    with open(full_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        csv_writer.writerow(["order_id", "placed_at", "description", "product_id", "name", "manufacturer", "expiry", "rate_per_unit", "quantity_ordered", "total_price"])
        
        for record in user_data:
            for item in record["items"]:
                csv_writer.writerow([record["order_id"], str(record["placed_at"]), record["description"], item["product_id"], item["name"], item["manufacturer"], str(item["expiry"]), item["rate_per_unit"], item["quantity_ordered"], item["total_price"]])

    return full_path
    
@shared_task(ignore_result=False)
def remainder(email):
    print("Hi")
    return send_email(email)


@shared_task(ignore_result=False)
def generate_report(user_id):
    email = User.query.get(user_id).email
    # report_html_content = send_report_in_mail(email)
    # pdf_bytes = generate_pdf(report_html_content)
    send_report_in_mail.delay(email)






