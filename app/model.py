from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, DateTime, desc
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

from app.db import get_db
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
      
    def delete(self):
        ses = get_db()
        ses.delete(self)
        ses.commit()
   
    @staticmethod
    def get_all():
        return get_db().query(User).all()

    @classmethod
    def get_by_id(cls, facebook_id):
        return get_db().query(User).filter(cls.fb_id == facebook_id).one_or_none()
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'fb_id': self.fb_id,
            'picture': self.picture,
            'joined': self.time_joined
        }


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.fb_id'))
    user = relationship(User)

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id, 
            'name': self.name
        }

    @property
    def menu_length(self):
        return len(MenuItem.get_restaurant_menu(self.id))

    def save(self):
        ses = get_db()
        ses.add(self)
        ses.commit()
        
    def delete(self):
        ses = get_db()
        ses.delete(self)
        ses.commit()

    
    @classmethod
    def get_all(cls):
        return get_db().query(Restaurant).order_by(cls.id.desc()).all()

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
    user_id = Column(Integer, ForeignKey('user.fb_id'))

    restaurant = relationship(Restaurant)
    user = relationship(User)

    # def __init__(self, name, course, description, price, restaurant_id, user_id):
    #     self.name = name
    #     self.course = course
    #     self.description = description
    #     self.price = price
    #     self.restaurant_id = restaurant_id
    #     self.user_id = user_id

    def save(self):
        ses = get_db()
        ses.add(self)
        ses.commit()
        
    def delete(self):
        ses = get_db()
        ses.delete(self)
        ses.commit()


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

    @classmethod
    def get_all(cls):
        return get_db().query(cls).order_by(cls.id).all()

    @classmethod
    def get_by_id(cls, id):
        return get_db().query(cls).filter_by(id = id).one_or_none()

    @classmethod
    def get_restaurant_menu(cls, id):
        return get_db().query(cls).filter(MenuItem.restaurant_id == id).order_by(desc(cls.id)).all()