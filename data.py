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

def add_post():
    with get_cursor(True) as cur:
        current_app.logger.info("Adding post data")
        cur.execute("insert into posts (author, content, place) values (%s, %s, %s)"), ('User', 'Filler Filler', '1 Valleyfair Dr Shakopee, MN')
    
def get_posts():
    with get_cursor() as cur:
        cur.execute("select * from posts")
        return cur.fetchall()