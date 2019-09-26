from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from restaurantszone.db import get_db

Base = declarative_base()
# declaring the object model of the table
class User(Base):
    
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    fb_id = Column(Integer, unique=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    picture = Column(String, nullable=False)
    time_joined = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, name, email, fb_id, picture):
        self.name = name
        self.email = email
        self.picture = picture
        self.fb_id = fb_id

    def save(self):
        s = get_db()
        s.add(self)
        s.commit()
   
    @staticmethod
    def get_all():
        return get_db().query(User).all()

    @staticmethod
    def get_by_id(id):
        return get_db().query(User).one_or_none()
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'joined': self.time_joined
        }


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