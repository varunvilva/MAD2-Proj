from api_application import *
from api_application.models import *
from api_application.worker import celery_init_app
import flask_excel as excel

celery_app = celery_init_app(app)  
if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    excel.init_excel(app)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.Security = Security(app,user_datastore)
    x = app.Security.datastore.find_or_create_role(name='admin', description='Administrator')
    y = app.Security.datastore.find_or_create_role(name='user', description='User')
    if not app.Security.datastore.find_user(username='Legeng'):
        app.Security.datastore.create_user(username='Legeng',email='example@gmail.com', password=hash_password('12345678'), roles=[x])

    db.session.commit()
    app.run(debug=True)