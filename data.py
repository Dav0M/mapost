import psycopg2
import os
import logging

from contextlib import contextmanager
from flask import g, current_app
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info("creating database connection pool")
    pool = ThreadedConnectionPool(1,20,dsn=DATABASE_URL,sslmode="require")

@contextmanager
def get_connection():
    try:
        conn = pool.getconn()
        yield conn
    finally:
        pool.putconn(conn)

@contextmanager
def get_cursor(commit=False):
    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        cursor.close()

def add_post(fd, img, id):
    with get_cursor(True) as cur:
        current_app.logger.info("Adding post data")
        imgData = img.read()
        imgBin = psycopg2.Binary(imgData)
        cur.execute("""insert into posts2 (user_id, content, img, geog) values
         (%s, %s, %s, ST_MakePoint(%s,%s))""", (id, fd["create-text"], imgBin, fd["create-long"], fd["create-lat"]))
    
def get_posts():
    with get_cursor() as cur:
        cur.execute("""select posts2.id, posts2.user_id, posts2.content, encode(posts2.img::bytea, 'base64') as "img",
         (ST_X(ST_AsText(posts2.geog)), ST_Y(ST_AsText(posts2.geog))) as "geog", posts2.time, users.name from posts2 
         inner join users on posts2.user_id=users.id;""")
        return cur.fetchall()

def get_userid(email):
    with get_cursor() as cur:
        cur.execute("select id from users where email = %s", (email,))
        return cur.fetchone()

def add_user(name, email, img):
    with get_cursor(True) as cur:
        cur.execute("insert into users (name, email, img) values (%s,%s,%s)", (name, email, img))

def update_user(name, email, img):
    with get_cursor(True) as cur:
        cur.execute("update users set name = %s, img = %s where email = %s", (name, img, email))
        return cur.rowcount