from api_application.models import *
from api_application.worker import celery_init_app
# from api_application.emails import send_email
import flask_excel as excel
from celery.schedules import crontab
from api_application.tasks import remainder
from api_application.auth import user_datastore 
from flask_mail import Mail

celery_app = celery_init_app(app)  

@celery_app.on_after_configure.connect
def sendEmail(sender, **kwargs):
    email = "varunvilva1208@gmail.com"
    sender.add_periodic_task(
        crontab(hour=15, minute=5, day_of_week='mon,tue,wed,thu,fri,sat,sun'),
        remainder.s(email),
    )
    


if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    excel.init_excel(app)
    app.Security = Security(app,user_datastore)
    app.Security.datastore.find_or_create_role(name='admin', description='Administrator')
    app.Security.datastore.find_or_create_role(name='user', description='User')
    app.Security.datastore.find_or_create_role(name='manager', description='Manager')
    if not app.Security.datastore.find_user(email='example@gmail.com'):
        app.Security.datastore.create_user(username='Legeng',email='example@gmail.com', password=hash_password("12345678"), roles=["admin"])
    if not app.Security.datastore.find_user(email="manager1@gmail.com"):
        app.Security.datastore.create_user(username='manager1',email="manager1@gmail.com", password=hash_password("12345678"), roles=["manager"],active=False)
    db.session.commit()
    app.run(debug=True)

#  celery -A run:celery_app beat --loglevel INFO