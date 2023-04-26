import os

from . import app
from os.path import join, exists
from json import dumps
from flask import Blueprint, request
from werkzeug.utils import secure_filename

from .modules.access_handler import access_handler

portfolio_router = Blueprint('portfolio', __name__, url_prefix='/portfolio')


@portfolio_router.post('/add')
@access_handler()
def add_portfolio(user):
    file = request.files.get('file')
    if not file.mimetype.startswith('image'):
        return dumps(
            {
                'message': 'Неопознанный формат файла, отправьте изображение!',
                'resultCode': 2
            },
            ensure_ascii=False), 200

    path = join(app.static_folder, 'portfolio', str(user['id']))
    if not exists(path):
        os.mkdir(path)

    filename = secure_filename(file.filename)
    file.save(join(app.static_folder, 'portfolio', str(user['id']), filename))
    return dumps({'message': 'Файл был добавлен!', 'resultCode': 0, 'filename': filename}, ensure_ascii=False), 200


@portfolio_router.post('/delete')
@access_handler()
def delete_portfolio(user):
    data = request.json
    if data is None or 'filename' not in data:
        return dumps({'message': 'Вы не передали данные #1!', 'resultCode': 2}, ensure_ascii=False), 200

    filename = data['filename']
    path = join(app.static_folder, 'portfolio', str(user['id']), filename)
    if not exists(path):
        return dumps({'message': 'Файл не найден!', 'resultCode': 2}, ensure_ascii=False), 200

    os.remove(path)
    return dumps({'message': 'Файл был удалён!', 'resultCode': 0}, ensure_ascii=False), 200