from . import app

import os
from json import dumps
from hashlib import sha256
from os.path import join, exists
from flask_cors import cross_origin
from flask import Blueprint, request, send_file

from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler, get_user

profile_router = Blueprint('profile', __name__, url_prefix='/profile')


@app.get('/profile')
@app.get('/auth/me')
@app.get('/profile/<username>')
def my_profile(username=None):
    db, sql = create_connect()
    if username is not None:
        sql.execute("""SELECT u.id, first_name, last_name, father_name, login, role_id, r.name role, birthday
                                FROM users u LEFT JOIN roles r on r.id = u.role_id WHERE u.login=%s""", (username,))
        user = sql.fetchone()
        if user is None:
            return dumps({'message': 'Профиль не найден!', 'resultCode': 2}, ensure_ascii=False), 200
    else:
        user = get_user(request.headers.get('Authorization'))
    sql.execute("SELECT id, title, description FROM contacts WHERE user_id=%s ORDER BY id", (user['id'],))
    contacts = sql.fetchall()

    sql.execute(
        "SELECT s.id, title  FROM user_directions ud INNER JOIN specialties s ON ud.direction_id = s.id WHERE ud.user_id=%s  ORDER BY s.id",
        (user['id'],))
    directions = sql.fetchall()

    sql.execute("SELECT COUNT(*) cnt FROM user_likes WHERE target_id=%s",(user['id'],))
    likes = sql.fetchone()['cnt']
    portfolio_path = join(app.static_folder, 'portfolio', str(user['id']))
    is_portfolio = exists(portfolio_path)
    portfolio = os.listdir(portfolio_path) if is_portfolio else []

    return dumps({
        'user': user,
        'contacts': contacts,
        'portfolio': portfolio,
        'directions': directions,
        'likes':likes
    }, ensure_ascii=False, default=str)


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
        return dumps({'message': 'Неопознанный формат файла, отправьте изображение!', 'resultCode': 2},
                     ensure_ascii=False), 200

    file.save(join(app.static_folder, 'avatars', f"{user.get('id')}.jpg"))
    return dumps({'message': 'Аватар был изменён!', 'resultCode': 0}, ensure_ascii=False), 200


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


@profile_router.post('/add-direction')
@access_handler()
def add_direction_to_user(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    keys = ('id',)

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()
    try:
        sql.execute("INSERT INTO user_directions (user_id, direction_id) VALUES (%s, %s)", (user['id'], data['id']))
    except:
        db.rollback()
        db.close()
        return dumps({'message': 'У вас уже выбрана эта тема!', 'resultCode': 2}, ensure_ascii=False)
    db.commit()
    db.close()
    return dumps({'message': 'Тема успешно добавлена!', 'resultCode': 0}, ensure_ascii=False), 200


@profile_router.post('/remove-direction')
@access_handler()
def remove_direction_from_user(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    keys = ('id',)

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("DELETE FROM user_directions WHERE user_id=%s AND direction_id=%s", (user['id'], data['id']))

    db.commit()
    db.close()
    return dumps({'message': 'Тема успешно удалена!', 'resultCode': 0}, ensure_ascii=False), 200


@profile_router.post('/like')
@access_handler()
def like_handler(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    keys = ('target_id','action')

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    if data['target_id'] == user['id']:
        return dumps({'message': 'Нельзя себе лайки ставить:(', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()
    try:
        if data['action'] == 'unset':
            sql.execute("DELETE FROM user_likes WHERE user_id=%s AND target_id=%s", (user['id'], data['target_id']))
        else:
            sql.execute("INSERT INTO user_likes (user_id, target_id) VALUES (%s, %s)", (user['id'], data['target_id']))
    except:
        db.close()
        return dumps({'message':'Во время выполнения запроса произошла ошибка!', 'resultCode':2}, ensure_ascii=False), 200
    db.commit()
    db.close()
    return dumps({'message': 'Успешно!', 'resultCode': 0}, ensure_ascii=False), 200


