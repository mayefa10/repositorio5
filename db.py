import sqlite3
from flask import current_app, g
from sqlite3 import Error


def get_db():
    try:
        if 'db' not in g:
            g.db = sqlite3.connect("registros_estudiantes.db")
            g.db.row_factory = sqlite3.Row
        return g.db
    except Error:
        print( Error )

def close_db():
    if g.db is not None:
        g.db.close()
