import os
from . import app
from os.path import join, exists
from json import dumps
from hashlib import sha256
from datetime import datetime
from random import randint, choices

from flask_cors import cross_origin
from flask import Blueprint, request

from .modules.confirm_mail import mail_send
from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler, get_user

auth_router = Blueprint('auth', __name__, url_prefix='/auth')


@auth_router.post('/login')
@cross_origin()
def get_login():
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json

    if 'login' not in data or 'password' not in data:
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    password = sha256(data.get('password').encode('utf-8')).hexdigest()
    sql.execute("SELECT u.id, first_name, last_name, father_name, login, role_id, r.name role "
                "FROM users u LEFT JOIN roles r on r.id = u.role_id WHERE login = %s AND password = %s",
                (data.get('login'), password))
    user = sql.fetchone()
    if user is None:
        return dumps({'message': 'Неверный логин или пароль!', 'resultCode': 2}, ensure_ascii=False), 200

    token = sha256(f"{password}{randint(0, 999)}{datetime.now().timestamp()}".encode('utf-8')).hexdigest()
    sql.execute("INSERT INTO sessions (token, user_id) VALUES (%s, %s)", (token, user['id']))
    db.commit()

    sql.execute("SELECT id, title, description FROM contacts WHERE user_id=%s ORDER BY id", (user['id'],))
    contacts = sql.fetchall()

    sql.execute(
        "SELECT s.id, title  FROM user_directions ud INNER JOIN specialties s ON ud.direction_id = s.id WHERE ud.user_id=%s  ORDER BY s.id",
        (user['id'],))
    directions = sql.fetchall()

    sql.execute("SELECT COUNT(*) cnt FROM user_likes WHERE target_id=%s", (user['id'],))
    likes = sql.fetchone()['cnt']
    portfolio_path = join(app.static_folder, 'portfolio', str(user['id']))
    is_portfolio = exists(portfolio_path)
    portfolio = os.listdir(portfolio_path) if is_portfolio else []

    db.close()

    return dumps({
        'user': user,
        'contacts': contacts,
        'portfolio': portfolio,
        'directions': directions,
        'likes':likes,
        'is_liked':False,
        'token': token
    }, ensure_ascii=False), 200


@auth_router.get('/logout')
@access_handler()
def do_logout(user):
    db, sql = create_connect()

    sql.execute('UPDATE sessions SET is_active=False WHERE token=%s', (request.headers.get('Authorization', ''),))
    db.commit()

    db.close()
    return dumps({'message': 'Logout success', 'resultCode': 0}), 200


@auth_router.post('/register')
@cross_origin()
def create_account():
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json
    code = data.get('code')

    keys = (
        'login', 'password', 'first_name', 'last_name', 'father_name', 'birthday', 'email'
    )

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200
    try:
        datetime.strptime(data['birthday'], '%Y-%m-%d')
    except ValueError:
        return dumps({'message': 'Некорректная дата рождения!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()

    sql.execute("SELECT id FROM mail_codes WHERE email=%s AND code=%s", (data['email'], code))
    if sql.rowcount == 0:
        db.close()
        return dumps({'message': 'Не верный код подтверждения!', 'resultCode': 2}, ensure_ascii=False), 200

    sql.execute('SELECT email, login FROM users WHERE login=%s OR email=%s', (data['login'], data['email']))
    result = sql.fetchone()

    if result is not None:
        db.close()
        if result['email'] == data['email']:
            return dumps({'message': 'Почта уже занята!', 'resultCode': 2}, ensure_ascii=False), 200
        return dumps({'message': 'Логин занят!', 'resultCode': 2}, ensure_ascii=False), 200

    data['password'] = sha256(data['password'].encode('utf-8')).hexdigest()

    sql.execute(
        f"INSERT INTO users ({', '.join(keys)}) VALUES ({(', %s' * len(keys))[2:]}) RETURNING id",
        (*(data[key] for key in keys),))

    user_id = sql.fetchone()['id']
    token = sha256(f"{data['password']}{randint(0, 999)}{datetime.now().timestamp()}".encode('utf-8')).hexdigest()
    sql.execute("INSERT INTO sessions (token, user_id) VALUES (%s, %s)", (token, user_id))
    db.commit()
    db.close()

    user = get_user(token)
    user['token'] = token
    return dumps(user, ensure_ascii=False, default=str), 200


@auth_router.post('/confirm-mail')
@cross_origin()
def confirm_mail():
    if request.json is None:
        return dumps({'message': 'Ошибка. Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    email = request.json.get('mail')
    code = ''.join(choices('0123456789', k=6))

    db, sql = create_connect()
    sql.execute("SELECT create_at FROM mail_codes WHERE email=%s", (email,))

    is_mail = sql.fetchone()
    if is_mail is None or (datetime.now() - is_mail['create_at']).seconds > 60:
        sql.execute("INSERT INTO mail_codes (email, code) VALUES (%s, %s)", (email, code))
        db.commit()
        mail_send(email, code)
        return dumps({'message': 'Письмо с кодом отправлено на почту!', 'resultCode': 0}, ensure_ascii=False), 200

    else:
        db.close()
        return dumps({'message': 'Код можно запрашивать раз в 5 минут!', 'resultCode': 2}, ensure_ascii=False), 200
