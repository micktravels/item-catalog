import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Setup the base class from which our other classes (tables) will inherit
Base = declarative_base()

class User(Base):
    __tablename__='user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    email = Column(String(80), nullable=False)
    picture = Column(String(100))


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    imgURL = Column(String(120))
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'imgURL': self.imgURL,
            'user_id': self.user_id
        }

class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    imgURL = Column(String(120))
    addDate = Column(DateTime)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
	#Returns object data in easily serializeable format
	return {
        'id': self.id,
	    'name': self.name,
	    'description': self.description,
	    'imgURL': self.imgURL,
        'user_id': self.user_id
	}

engine = create_engine('sqlite:///catalog.db')

# Adds our classes as new tables in database
Base.metadata.create_all(engine)
