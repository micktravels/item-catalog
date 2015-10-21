import datetime
from random import randint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

def CreateRandomAge():
       rightnow = datetime.datetime.now()
       days_old = randint(0,30)
       entryday = rightnow - datetime.timedelta(days = days_old)
       return entryday

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
category1 = Category(user_id=1, name="Cameras", imgURL="")

session.add(category1)
session.commit()

item2 = Item(user_id=1, name="Canon", description="New image stabilization", imgURL="", addDate=CreateRandomAge(), category=category1)

session.add(item2)
session.commit()


item2 = Item(user_id=1, name="Polaroid", description="Old standard", imgURL="", addDate=CreateRandomAge(), category=category1)

session.add(item2)
session.commit()

print "added items!"

