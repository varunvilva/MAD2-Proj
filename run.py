from api_application.models import *
from api_application.worker import celery_init_app
# from api_application.emails import send_email
import flask_excel as excel
from celery.schedules import crontab
from api_application.tasks import *
from api_application.auth import user_datastore 
from flask_mail import Mail
from datetime import datetime as dt
from datetime import timedelta

celery_app = celery_init_app(app)  

@celery_app.on_after_configure.connect
def sendEmail(sender, **kwargs):
    app.app_context().push()
    for user in User.query.all():
        role = Role.query.filter_by(id = RolesUsers.query.filter_by(id=user.id).first().role_id).first().name
        if role == "user" and user.active == True:
            if(user.last_login_time == None or dt.utcnow()-user.last_login_time>timedelta(days=1)):
                email = user.email
                sender.add_periodic_task(
                    crontab(hour='*', minute='*', day_of_week='*'),
                    # crontab(hour='0', minute='30', day_of_week='*'),
                    remainder.s(email),
                )

@celery_app.on_after_configure.connect
def generate_monthly_report(sender, **kwargs):
    # Configure the periodic task to run generate_monthly_report at the end of each month
    for user in User.query.all():
        role = Role.query.filter_by(id = RolesUsers.query.filter_by(id=user.id).first().role_id).first().name
        if role == "user" and user.active == True:
            user_id = user.id
            sender.add_periodic_task(
                crontab(day_of_month='*', hour='*', minute='*',day_of_week='*'),
                generate_report.s(user_id=user_id),  # Change the user_id as needed   
                name=f'generate-monthly-report-{user_id}'
            )
            print(user.email)
    
    

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    excel.init_excel(app)
    app.Security = Security(app,user_datastore)
    app.Security.datastore.find_or_create_role(name='admin', description='Administrator')
    app.Security.datastore.find_or_create_role(name='user', description='User')
    app.Security.datastore.find_or_create_role(name='manager', description='Manager')
    if not app.Security.datastore.find_user(email='dcvarunv@gmail.com'):
        app.Security.datastore.create_user(username='Legeng',email='dcvarunv@gmail.com', password=hash_password("12345678"), roles=["admin"])
    db.session.commit()
    app.run(debug=True)

#  celery -A run:celery_app beat --loglevel INFO
#  celery -A run:celery_app worker --loglevel INFO