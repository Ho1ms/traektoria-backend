import psycopg2.extras
from os import getenv


def create_connect():
    db = psycopg2.connect(
        host=getenv('db_host'),
        database=getenv('db_name'),
        user=getenv('db_user'),
        password=getenv('db_password')
    )
    sql = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return db, sql