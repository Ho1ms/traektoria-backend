from json import dumps
from flask import Blueprint

from .modules.database import create_connect
from .modules.access_handler import access_handler

users_router = Blueprint('users', __name__, url_prefix='/users')


@users_router.get('/')
@access_handler(1)
def get_roles(user):
    db, sql = create_connect()

    sql.execute("SELECT id, first_name, last_name, father_name FROM users")
    rows = sql.fetchall()

    db.close()
    return dumps(rows, ensure_ascii=False), 200

