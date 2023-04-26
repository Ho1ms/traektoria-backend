from . import app
from json import dumps
from flask import Blueprint
from flask_cors import cross_origin
from .modules.database import create_connect

users_router = Blueprint('users', __name__, url_prefix='/users')


@app.get('/users')
@cross_origin()
def get_roles():
    db, sql = create_connect()

    sql.execute("SELECT id, first_name, last_name, father_name FROM users")
    rows = sql.fetchall()

    db.close()
    return dumps(rows, ensure_ascii=False), 200

