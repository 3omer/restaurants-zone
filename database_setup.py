import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


Base = declarative_base()

# declaring the object model of the table

class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    def __str__(self):
        return "id: %s - name: %s" % (self.id, self.name)


class MenuItem(Base):
    __tablename__ = "menu_item"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    resturant = relationship(Restaurant)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'course': self.course,
            'description': self.description,
            'price': self.price
        }

    def __str__(self):
        return "id: %s - name: %s - price: %s - restaurant: %s" % (self.id, self.name, self.price, self.resturant.name)


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)