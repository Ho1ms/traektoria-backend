import logging
from os import getenv
import os
from flask import Flask, send_file
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

load_dotenv()


def get_folder(*folders):
    return os.path.join(os.getcwd(), *folders)


app = Flask('TRAEKTORIA', static_folder=get_folder('app','static'))
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

CORS(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


from .auth import auth_router
app.register_blueprint(auth_router)

from .profile import profile_router
from .contacts import contacts_router
from .portfolio import portfolio_router

profile_router.register_blueprint(portfolio_router)
profile_router.register_blueprint(contacts_router)
app.register_blueprint(profile_router)

from .users import users_router
app.register_blueprint(users_router)

from .admin import admin_router
app.register_blueprint(admin_router)

from .directions import direction_router
app.register_blueprint(direction_router)

from .news import news_router
app.register_blueprint(news_router)
