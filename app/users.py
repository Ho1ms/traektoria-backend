from . import app
from json import dumps
from flask import Blueprint, request
from flask_cors import cross_origin
from .modules.database import create_connect

users_router = Blueprint('users', __name__, url_prefix='/users')


@app.get('/users')
@cross_origin()
def get_roles():
    db, sql = create_connect()
    query = '%' + request.args.get('q','') + '%'
    q = ''
    args = ()
    if request.args.get('q') is not None:
        q = "WHERE CONCAT(last_name,' ',first_name ,' ',father_name,' ', login) LIKE %s"
        args = (query,)
    sql.execute(f"""SELECT * FROM (
    SELECT users.id, first_name, last_name, father_name, login, count(ul.target_id) likes
        FROM users LEFT JOIN user_likes ul on users.id = ul.target_id {q}
        GROUP BY users.id, first_name, last_name, father_name, login ) t ORDER BY likes DESC, id  """, args)
    rows = sql.fetchall()

    db.close()
    return dumps(rows, ensure_ascii=False), 200

