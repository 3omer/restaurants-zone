from sqlalchemy import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from flask import current_app, g
from flask.cli import click
from flask.cli import with_appcontext

Base = declarative_base()

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


# declaring the object model of the table

class User(Base):
    
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    picture = Column(String, nullable=False)
    time_joined = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'joined': self.time_joined
        }

    @staticmethod
    def get_all():
        return get_db().query(User).all()

    @staticmethod
    def get_by_id(id):
        return get_db().query(User).one_or_none()

class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id, 
            'name': self.name
        }
    
    @staticmethod
    def get_all():
        return get_db().query(Restaurant).all()

    @staticmethod
    def get_by_id(id):
        return get_db().query(Restaurant).filter_by(id = id).one_or_none()


class MenuItem(Base):
    __tablename__ = "menu_item"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    restaurant = relationship(Restaurant)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'course': self.course,
            'description': self.description,
            'price': self.price
        }

    @staticmethod
    def get_all():
        return get_db().query(MenuItem).all()

    @staticmethod
    def get_by_id(id):
        return get_db().query(MenuItem).filter_by(id = id).one_or_none()



def init_db():
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

