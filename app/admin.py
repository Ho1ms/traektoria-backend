from json import dumps
from flask import Blueprint

from .modules.database import create_connect
from .modules.access_handler import access_handler

admin_router = Blueprint('admin', __name__, url_prefix='/admin')


@admin_router.get('/roles')
@access_handler(1)
def get_roles(user):
    db, sql = create_connect()

    sql.execute("SELECT id, name FROM roles")
    rows = sql.fetchall()

    db.close()
    return dumps(rows, ensure_ascii=False), 200


@admin_router.get('/users')
@access_handler(1)
def get_admin_users(user):
    db, sql = create_connect()

    sql.execute("SELECT u.id, login, first_name, last_name, father_name, email, role_id, r.name role, birthday FROM users u INNER JOIN roles r ON r.id = u.role_id")
    rows = sql.fetchall()

    db.close()
    return dumps(rows, ensure_ascii=False, default=str), 200

