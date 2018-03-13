from flask import Flask, Blueprint, render_template, url_for, session, redirect
#from app.db_connections import create_session
#from app.models import *

#dbs = create_session()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session['user_id'] or session['user_id'] is None:
            return redirect(url_for('users.login'))
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)
app.config['SERVER_NAME'] = 'kridder.eu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "despokesonthewheelgoroundandround"
app.config['WTF_CRSF_ENABLED'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

#@app.before_request
#def before_request():
#    if not 'user_id' in session.keys():
#        session['user_id'] = None


from app.views import default, music, ion, tests
#from app.linker import linker
#from app.users import users
#from app.mm import mm
#from app.ion import ion

app.register_blueprint(default)
app.register_blueprint(music)
app.register_blueprint(ion)
app.register_blueprint(tests)
#app.register_blueprint(ion)

from app import views
