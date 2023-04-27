from . import app
from json import dumps
from flask import Blueprint, request
from flask_cors import cross_origin
from .modules.database import create_connect
from .modules.access_handler import get_user
users_router = Blueprint('users', __name__, url_prefix='/users')


@app.get('/users')
@cross_origin()
def get_roles():
    db, sql = create_connect()
    query = '%' + request.args.get('q','') + '%'
    q = ''
    auth = request.headers.get('Authorization')
    user = None
    if auth is not None:
        user = get_user(auth)

    args = (user['id'] if user else None,)
    if request.args.get('q') is not None:
        q = "WHERE CONCAT(last_name,' ',first_name ,' ',father_name,' ', login) LIKE %s"
        args = (query,user['id'] if user else None)
    sql.execute(f"""SELECT t.id, first_name, last_name, father_name, login, likes,  (u.id is not null) as is_liked FROM (
    SELECT users.id, first_name, last_name, father_name, login, count(ul.target_id) likes
        FROM users LEFT JOIN user_likes ul on users.id = ul.target_id {q}
        GROUP BY users.id, first_name, last_name, father_name, login ) t LEFT JOIN user_likes u ON target_id=t.id AND user_id=%s ORDER BY likes DESC, id  """, args)
    rows = sql.fetchall()

    # Жоска заговнокодили ибо времени нет
    for row in rows:
        sql.execute("SELECT s.id, s.title FROM specialties s INNER JOIN user_directions ud on s.id = ud.direction_id WHERE user_id=%s", (row['id'],))
        row['directions'] = sql.fetchall()
        
    db.close()
    return dumps(rows, ensure_ascii=False), 200

