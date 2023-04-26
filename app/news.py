from . import app

import os
from json import dumps
from hashlib import sha256
from os.path import join, exists
from flask import Blueprint, request
from random import randint
from datetime import datetime
from .modules.database import create_connect
from .modules.validator import validate_data
from .modules.access_handler import access_handler, get_user

news_router = Blueprint('news', __name__, url_prefix='/news')


@news_router.get('/')
def get_news_list():
    user = get_user(request.headers.get('Authorization'))
    db, sql = create_connect()
    news = []
    if user:
        sql.execute("""SELECT * FROM (SELECT news.id, author_id, concat(u.last_name, ' ', u.first_name) as author_name, title, description, to_char(create_at, 'HH24:MM dd.mm.YYYY') create_at, attachment FROM news
                            INNER JOIN news_tags nt on news.id = nt.news_id AND direction_id = ANY(SELECT direction_id FROM user_directions WHERE user_id=%s)
                            LEFT JOIN users u ON author_id=u.id) t GROUP BY id, author_id, author_name, title, description, attachment, create_at""",
                    (user['id'],))
        news = sql.fetchall()
    if len(news) == 0:
        sql.execute("""SELECT news.id, author_id, concat(u.last_name, ' ', u.first_name) as author_name, title, description,  to_char(create_at, 'HH24:MM dd.mm.YYYY') create_at, attachment FROM news
    INNER JOIN users u ON author_id=u.id""")
        news = sql.fetchall()

    return dumps(news, ensure_ascii=False, default=str), 200


@news_router.post('/add')
@access_handler(1, 4)
def add_news(user):
    if request.form is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.form

    keys = (
        'title', 'description'
    )

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    file = request.files.get('file')
    filename = None
    if file:
        if not file.mimetype.startswith('image'):
            return dumps(
                {
                    'message': 'Неопознанный формат файла, отправьте изображение!',
                    'resultCode': 2
                },
                ensure_ascii=False), 200

        path = join(app.static_folder, 'news')
        if not exists(path):
            os.mkdir(path)

        filename = sha256(
            f"{file.filename}{datetime.now().timestamp()}{randint(0, 999)}".encode('utf-8')).hexdigest() + '.jpg'
        file.save(join(app.static_folder, 'news', filename))

    db, sql = create_connect()
    sql.execute("INSERT INTO news (title, description, author_id, attachment) VALUES (%s, %s, %s, %s) RETURNING id",
                (data['title'], data['description'], user['id'], filename))
    id = sql.fetchone()['id']
    db.commit()
    db.close()
    return dumps({
        'id': id,
        'title': data['title'],
        'description': data['description'],
        'attachment': filename
    }, ensure_ascii=False, default=str), 200


@news_router.post('/delete')
@access_handler(1, 4)
def delete_news(user):
    if request.json is None:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    data = request.json

    keys = (
        'id',
    )

    if not validate_data(data, keys):
        return dumps({'message': 'Вы не передали данные #2!', 'resultCode': 2}, ensure_ascii=False), 200

    db, sql = create_connect()
    sql.execute("DELETE FROM news WHERE id =%s AND author_id=%s", (data['id'],user['id']))
    is_delete = sql.rowcount
    db.commit()
    db.close()
    if is_delete == 0:
        return dumps({'message': 'Можно удалять только свои новости!', 'resultCode': 2}, ensure_ascii=False), 200
    return dumps({'message': 'Новость удалена!', 'resultCode': 0}, ensure_ascii=False), 200
