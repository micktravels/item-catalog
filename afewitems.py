import datetime
import psycopg2
from random import randint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

# We're moving from sqlite to postgresql
# engine = create_engine('sqlite:///catalog.db')
# new engine command follows this syntax:
#    dialect+driver://username:password@host:port/database
engine = create_engine('postgresql+psycopg2://catalog:Adm9ZHtw52pcGDGeWmZY@localhost/catalog')

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
category = Category(user_id=1, name="Kitchen")

session.add(category)
session.commit()

item = Item(user_id=2, name="Cheese Straightener", description="Miniature Multi Purpose Cheese Pipe Straightener, to straighten your bent cheese.  " + 
	"Areas of Application: straightens all types and flavors of cheese.", imgURL="http://www.in.all.biz/img/in/catalog/616893.png", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()


item = Item(user_id=1, name="Spoon Rest", description="Oversized Stainless Steel Spoon Rest. Beauty and function find this 18/8 polished spoon rest " +
	"ever present in the cooks space ", imgURL="http://ecx.images-amazon.com/images/I/31VBC7MA7EL.jpg",
	addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()


item = Item(user_id=1, name="Asparagus Peeler", description="" + 
	" The peeler may also be used to snip the ends of green beans and sugar snap peas.",  imgURL="http://ecx.images-amazon.com/images/I/715AMKclk-L._SL1500_.jpg",
	addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()

item = Item(user_id=1, name="MDF200 Automatic Mini Donut Factory", description="Makes up to 30 perfectly-sied mini donuts per batch.  " + 
	"Stainless steel spatulas turn and delivers donuts to the dispensing chute",  imgURL="http://ecx.images-amazon.com/images/I/71LYzCtXsuL._SL1500_.jpg",
	addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()

# Populate Category 2
category = Category(user_id=2, name="High-Tech")

session.add(category)
session.commit()

item = Item(user_id=2, name="DVD Rewinder", description="The DVD Rewinder works with all disc based digital media to provide optimized digital experience.  " + 
#	"Visual indicators blink and audible sounds are played while your digital media is 'reversed.'  " +
#	"The DVD Rewinder also has a USB port for MP3 players and USB media.  " +
	"You can record your own sounds that play during rewind or use the digital recorder to store reminders.  ",
	imgURL="http://farm1.static.flickr.com/129/409584733_4b5f57f338_o.jpg", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()


item = Item(user_id=1, name="Toilet Roll iPod Dock", description="You'll never miss a song even in the bathroom with Atech's 'iLounge hybrid toilet paper dispenser/iPod dock'.  " + 
#	"The iLounge supports all iPod models that have a dock connector and has an integrated USB slot for the Shuffle.  " +
	"Speakers are concealed in the dispenser's arms with navigation buttons located conveniently on top for easy access.",
	imgURL="http://farm1.static.flickr.com/184/409584740_9acb1dd52d_o.jpg", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()


item = Item(user_id=1, name="360-Degree Camera", description="For those who wish to take the ultimate panoramic picture, look no furthur than this 360-degree camera.  " + 
	"It fits comfortably on your head and conveniently uses disposable cameras.",
	imgURL="http://farm1.static.flickr.com/162/409584927_330d192d0a_o.jpg", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()


item = Item(user_id=2, name="Defusable Bomb Alarm Clock", description="Time Bomb shaped design perfect for heavy sleepers.  " + 
	"In game mode, player is required to defuse the bomb by taking away correct one of the 4 wires within the 10 second countdown.  " +
#	"Alarm clock function - 4 digital clock display (in 24 hr format)  " +
	"Contains built-in rechargeable battery and USB port.  ",
	imgURL="http://ecx.images-amazon.com/images/I/41PoPdjTQ6L.jpg", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()

# Third Category
category = Category(user_id=2, name="Office")

session.add(category)
session.commit()

item = Item(user_id=2, name="That's Bullshit Button", description="The That's Bullshit Button is the preferred method of calling someone out on BS, when they start spewing ridiculous lies!  " + 
#	"Batteries are included with the Bullshit sound effects button!  Features 5 Bullshit phrases.  " +
#	"The DVD Rewinder also has a USB port for MP3 players and USB media.  " +
	"The giant red button talks the talk, lights up, flashes and even includes multiple background sound effects.  ",
	imgURL="http://ecx.images-amazon.com/images/I/81JeYrkECwL._SL1500_.jpg", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()


item = Item(user_id=1, name="Rubber Band Machine Gun", description="Rapid fire - 10 rounds per second.  " + 
	"Single squeeze motor-driven firing.  Holds 63 rubber bands.  ",
	imgURL="http://ecx.images-amazon.com/images/I/71Uwt7IYD1L._SL1500_.jpg", addDate=CreateRandomAge(), category=category)

session.add(item)
session.commit()

print "added items!"

