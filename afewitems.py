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
user = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user)
session.commit()

user = User(name="M Fink", email="mick@micktravels.com")
session.add(user)
session.commit()

# Populate Category 1
category1 = Category(user_id=1, name="Kitchen", imgURL="")

session.add(category1)
session.commit()

item = Item(user_id=2, name="Cheese Straightener", description="Miniature Multi Purpose Cheese Pipe Straightener, to straighten your bend cheese pipe." + 
	"Areas of Application: straightens all types and flavors of cheese", imgURL="http://www.in.all.biz/img/in/catalog/616893.png", addDate=CreateRandomAge(), category=category1)

session.add(item)
session.commit()


item = Item(user_id=1, name="Spoon Rest", description="Oversized Stainless Steel Spoon Rest. Beauty and function find this 18/8 polished spoon rest " +
	"ever present in the cooks space ", imgURL="http://ecx.images-amazon.com/images/I/31VBC7MA7EL.jpg",
	addDate=CreateRandomAge(), category=category1)

session.add(item)
session.commit()


item = Item(user_id=1, name="Asparagus Peeler", description="" + 
	" The peeler may also be used to snip the ends of green beans and sugar snap peas.",  imgURL="http://ecx.images-amazon.com/images/I/715AMKclk-L._SL1500_.jpg",
	addDate=CreateRandomAge(), category=category1)

session.add(item)
session.commit()


print "added items!"

