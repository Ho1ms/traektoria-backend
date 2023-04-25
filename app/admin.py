from json import dumps
from flask import Blueprint, request
from psycopg2.errors import ForeignKeyViolation
from .modules.database import create_connect
from .modules.validator import validate_data
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

@admin_router.get('/update_user/role')
@access_handler(1)
def update_role(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    keys = ('user_id', 'role_id')

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()
    try:
        sql.execute("UPDATE users SET role_id = %s WHERE id=%s", (data['role_id'], data['user_id']))
    except ForeignKeyViolation:
        db.rollback()
        db.close()
        return dumps({'message': 'Роль не найдена!', 'resultCode': 2}, ensure_ascii=False), 200

    db.commit()
    db.close()

    return dumps({'message':'Роль пользователя обновлена!', 'resultCode':0}, ensure_ascii=False), 200



