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
    
def get_posts(fd=None, page=1):
    with get_cursor() as cur:
        current_app.logger.info("Getting feed post data")
        if fd is None:
            cur.execute("""select posts2.id, posts2.user_id, posts2.content, encode(posts2.img::bytea, 'base64') as "img",
                (ST_X(ST_AsText(posts2.geog)), ST_Y(ST_AsText(posts2.geog))) as "geog", posts2.time, users.name, users.img as user_img from posts2 
                inner join users on posts2.user_id=users.id order by posts2.time desc limit 10 offset %s""", ((page-1)*10,))
        else:
            cur.execute("""select posts2.id, posts2.user_id, posts2.content, encode(posts2.img::bytea, 'base64') as "img",
                (ST_X(ST_AsText(posts2.geog)), ST_Y(ST_AsText(posts2.geog))) as "geog", posts2.time, users.name, users.img as user_img from posts2 
                inner join users on posts2.user_id=users.id 
                order by ST_Distance(posts2.geog, ST_MakePoint(%s,%s)) limit 10 offset %s""", (fd["create-long"], fd["create-lat"], (page-1)*10))
        return cur.fetchall()

def get_userid(email):
    with get_cursor() as cur:
        current_app.logger.info("Getting user ID data")
        cur.execute("select id from users where email = %s", (email,))
        return cur.fetchone()

def add_user(name, email, img):
    with get_cursor(True) as cur:
        current_app.logger.info("Adding new user data")
        cur.execute("insert into users (name, email, img) values (%s,%s,%s)", (name, email, img))

def update_user(name, email, img):
    with get_cursor(True) as cur:
        current_app.logger.info("Updating user data")
        cur.execute("update users set name = %s, img = %s where email = %s", (name, img, email))
        return cur.rowcount

def get_total(id=-1):
    with get_cursor() as cur:
        current_app.logger.info("Getting total posts")
        if (id == -1):
            cur.execute("select count(*) from posts2 inner join users on posts2.user_id=users.id")
        else:
            cur.execute("select count(*) from posts2 inner join users on posts2.user_id=users.id where posts2.user_id=%s", (id,))
        return cur.fetchone()

def get_users_posts(user_id, page=1):
    with get_cursor() as cur:
        current_app.logger.info("Getting users post data")
        cur.execute("""select posts2.id, posts2.user_id, posts2.content, encode(posts2.img::bytea, 'base64') as "img",
            (ST_X(ST_AsText(posts2.geog)), ST_Y(ST_AsText(posts2.geog))) as "geog", posts2.time, users.name, users.img as user_img from posts2 
            inner join users on posts2.user_id=users.id where posts2.user_id=%s order by posts2.time desc limit 10 offset %s""", (user_id,(page-1)*10))

def update_post(fd, img, post_id):
    with get_cursor(True) as cur:
        current_app.logger.info("Updating single post data")
        imgData = img.read()
        imgBin = psycopg2.Binary(imgData)
        cur.execute("update posts2 set content=%s, img=%s, geog=ST_MakePoint(%s,%s) where id=%s", (fd['create-text'], imgBin, fd["create-long"], fd["create-lat"], post_id))

def delete_post(post_id):
    with get_cursor(True) as cur:
        current_app.logger.info("Deleting single post data")
        cur.execute("delete from posts2 where id=%s", (post_id,))
        return cur.rowcount