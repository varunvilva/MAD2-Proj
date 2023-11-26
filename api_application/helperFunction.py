from api_application import mail
from flask_mail import Message
from .models import *
from flask import render_template
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from celery import shared_task

def send_email(email):
    sender = 'noreply@app.com'
    subject = "🌟 Don't Miss Out on the Fun! Your App Awaits Your Glorious Presence! 🚀"
    msg = Message(subject = subject, sender = sender, recipients = [email])
    msg.body="" 
    username = User.query.filter_by(email=email).first().username
    data = {
        'app_name':"Grocerify",
        "title":f"Hey {username},",
    }
    msg.html = render_template('email.html',data=data)
    try:
        mail.send(msg)
        return {"message":f"Email sent successfully to {email}"}, 200
    except Exception as e:
        return(str(e))

@shared_task(ignore_results=False)
def send_report_in_mail(email):
    sender = 'noreply@app.com'
    subject = "Monthly Repoprt of your activity"
    msg = Message(subject = subject, sender = sender, recipients = [email])
    msg.body=""
    username = User.query.filter_by(email=email).first().username
    user_id = User.query.filter_by(email=email).first().id
    data = {
        'app_name':"Grocerify",
        "title":f"Hey {username},",
    }
    report_html_content = get_user_activity_report(user_id)
    pdf_bytes = generate_pdf(report_html_content)

    msg.attach(
        filename='user_report.pdf',
        content_type='application/pdf',
        data=pdf_bytes.getvalue()
    )
    msg.html = render_template('email_report.html', data=data)
    try:
        mail.send(msg)
        print(f"Email sent successfully to {email}")
    except Exception as e:
        return(str(e))

def generate_pdf(html_content):
    from weasyprint import HTML
    pdf_bytes = BytesIO()
    HTML(string=html_content).write_pdf(pdf_bytes)
    return pdf_bytes

def get_user_activity_report(user_id):
    user = User.query.get(user_id)
    orders = Order.query.filter_by(user_id=user_id).all()

    
    order_dates = [order.placed_at.strftime('%Y-%m-%d') for order in orders]
        
    order_counts = [ OrderItem.query.filter_by(order_id = order.id).count() for order in orders]

    
    product_categories=[]
    for order in orders:
        for items in OrderItem.query.filter_by(order_id = order.id).all():
            product_categories.append(Product.query.filter_by(id = items.product_id).first().category.name)
    category_counts = {category: product_categories.count(category) for category in set(product_categories)}

    
    order_values = [sum([item.total_price for item in order.items]) for order in orders]
    average_order_values = [sum(order_values[:i + 1]) / (i + 1) for i in range(len(order_values))]

    
    activity_chart = save_bar_chart(order_dates, order_counts, 'User Activity', 'Date', 'Number of Orders')
    preferences_chart = save_bar_chart(list(category_counts.keys()), list(category_counts.values()), 'Product Preferences', 'Product Category', 'Number of Purchases')
    avg_order_chart = save_line_chart(order_dates, average_order_values, 'Average Order Value', 'Date', 'Average Order Value')

    return render_template(
        'report.html',
        user=user,
        activity_chart=activity_chart,
        preferences_chart=preferences_chart,
        avg_order_chart=avg_order_chart
    )

def save_bar_chart(x_data, y_data, title, x_label, y_label):
    plt.bar(x_data, y_data, color='blue')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    chart_stream = BytesIO()
    plt.savefig(chart_stream, format='png')
    chart_stream.seek(0)
    chart_data = base64.b64encode(chart_stream.read()).decode('utf-8')
    plt.close()

    return chart_data

def save_line_chart(x_data, y_data, title, x_label, y_label):
    plt.plot(x_data, y_data, color='green', marker='o')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    chart_stream = BytesIO()
    plt.savefig(chart_stream, format='png')
    chart_stream.seek(0)
    chart_data = base64.b64encode(chart_stream.read()).decode('utf-8')
    plt.close()

    return chart_data
