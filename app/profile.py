from . import app

from json import dumps
from hashlib import sha256
from os.path import join, exists
from flask_cors import cross_origin
from flask import Blueprint, request, send_file

from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler

profile_router = Blueprint('profile', __name__, url_prefix='/profile')


@app.get('/avatar/<int:user_id>')
@cross_origin()
def get_avatar(user_id):

    path = join(app.static_folder, 'avatars', f"{user_id}.jpg")
    if not exists(path):
        path = join(app.static_folder, 'avatars', f"unknown.jpg")

    return send_file(path)

@profile_router.post('/set-avatar')
@access_handler()
def set_my_avatar(user):
    file = request.files.get('avatar')
    if not file.mimetype.startswith('image'):
        return dumps({'message': 'Неопознанный формат файла, отправьте изображение!', 'resultCode': 2}, ensure_ascii=False), 200

    file.save(join(app.static_folder, 'avatars', f"{user.get('id')}.jpg"))
    return dumps({'message':'Аватар был изменён!','resultCode':0}, ensure_ascii=False), 200

@profile_router.post('/update')
@access_handler()
def update_my_profile(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    keys = ('first_name', 'last_name', 'father_name', 'birthday')

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute(
        f"UPDATE users SET {'=%s, '.join(keys)}=%s WHERE id=%s",
        (*(data[key] for key in keys), user['id']))

    db.commit()
    db.close()
    return dumps({'message': 'Данные успешно обновлены!', 'resultCode': 0}, ensure_ascii=False), 200


@profile_router.post('/change_password')
@access_handler()
def update_my_password(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    keys = ('password_1', 'password_2')

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    if data['password_1'] != data['password_2']:
        return dumps({'message': 'Пароли не совпадают!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("UPDATE users SET password = %s WHERE id = %s",
                (sha256(data['password_1'].encode('utf-8')).hexdigest(), user['id']))
    db.commit()
    db.close()
    return dumps({'message': 'Пароль успешно обновлён!', 'resultCode': 0}, ensure_ascii=False), 200