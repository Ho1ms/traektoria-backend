from json import dumps
from flask import Blueprint, request

from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler

direction_router = Blueprint('directions', __name__, url_prefix='/directions')


@direction_router.get('/')
def get_directions():
    db, sql = create_connect()
    sql.execute("SELECT * FROM specialties")
    rows = sql.fetchall()

    db.close()
    return dumps(rows, ensure_ascii=False), 200


@direction_router.post('/add')
@access_handler(1)
def add_direction(user):
    data = request.json

    if data is None or not validate_data(data, ('title', 'description')):
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("INSERT INTO specialties (title, description) VALUES ( %s, %s) RETURNING id",
                (data['title'], data['description']))
    direction_id = sql.fetchone()['id']

    db.commit()
    db.close()

    return dumps({
        'id': direction_id,
        'title': data['title'],
        'description': data['description']
    }, ensure_ascii=False, default=str)


@direction_router.post('/update')
@access_handler(1)
def update_contacts(user):
    data = request.json

    if data is None or not validate_data(data, ('id', 'title', 'description')):
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("UPDATE specialties SET title=%s, description=%s WHERE id=%s ",
                (data['title'], data['description'], data['id']))

    is_update = sql.rowcount
    db.commit()
    db.close()

    if is_update == 0:
        return dumps({'message': 'Запись с данными не найдена', 'resultCode': 2}, ensure_ascii=False), 200

    return dumps({
        'id': data['id'],
        'title': data['title'],
        'description': data['description']
    }, ensure_ascii=False, default=str)
