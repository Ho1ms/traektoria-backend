from json import dumps
from flask import Blueprint, request

from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler

contacts_router = Blueprint('contacts', __name__, url_prefix='/contacts')


@contacts_router.post('/add')
@access_handler()
def add_contacts(user):
    data = request.json

    if data is None or not validate_data(data, ('title', 'description')):
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("INSERT INTO contacts (user_id, title, description) VALUES (%s, %s, %s) RETURNING id",
                (user['id'], data['title'], data['description']))
    contact_id = sql.fetchone()['id']

    db.commit()
    db.close()

    return dumps({
        'id': contact_id,
        'title': data['title'],
        'description': data['description']
    }, ensure_ascii=False, default=str)


@contacts_router.post('/update')
@access_handler()
def update_contacts(user):
    data = request.json

    if data is None or not validate_data(data, ('id', 'title', 'description')):
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("UPDATE contacts SET title=%s, description=%s WHERE id=%s AND user_id=%s",
                (data['title'], data['description'], data['id'], user['id'],))
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


@contacts_router.post('/delete')
@access_handler()
def delete_contacts(user):
    data = request.json

    if data is None or 'id' not in data:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("DELETE FROM contacts WHERE id=%s AND user_id=%s",
                ( data['id'], user['id'],))
    is_delete = sql.rowcount
    db.commit()
    db.close()

    if is_delete == 0:
        return dumps({'message': 'Запись с данными не найдена', 'resultCode': 2}, ensure_ascii=False), 200

    return dumps({'message':'Запись успешно удалена!','resultCode':0}, ensure_ascii=False, default=str)

