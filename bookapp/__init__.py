from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail,Message
csrf = CSRFProtect()

mail = Mail()
def create_app():
    from bookapp.models import db
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile("config.py", silent=True)
    db.init_app(app)
    migrate = Migrate(app,db)
    csrf.init_app(app)
    mail.init_app(app)
    return app


  
#instantiate an object of flask so that it can easily be imported by othe modules in the package

        
app = create_app()
#load the route here
from bookapp import admin_routes, user_routes
from bookapp.forms import *
