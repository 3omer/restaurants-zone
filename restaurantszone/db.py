from sqlalchemy import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from flask import current_app, g
from flask.cli import click
from flask.cli import with_appcontext

def get_engine():
    return create_engine('sqlite:///' + current_app.config['DATABASE'])


def get_db():
    if 'db' not in g:
        db = Session(get_engine())
        g.db = db
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    from restaurantszone.model import Base
    engine = get_engine()
    Base.metadata.bind = engine
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)



@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Database initialized.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

