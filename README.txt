Welcome to the P3 Item Catalog application.

## Section 0 Intro
This application offers the user a handy way to store items in a catalog
via categories.

Features Supported:
	Google and Facebook OAuth 2.0 login
	Creation of Categories and Items if you are logged in
	Editing and Deleting of Item if you are logged in AND you own the Items
	Image support for Items
	Bootstrap Modal support for editing, creating, deleting, and logi
	JSON and XML data (via <URL>/JSON and <URL>/XML)
	pre-populated database of exciting items in popular categories
	Smart use of nested html templates to reduce coding
	CSRF protection for all POST requests

## Section 1 Setup Environment

How to run:
	Bring Vagrant VM up
	> python application.py
	http://localhost:8000
	ENJOY!

Comes with database populator tool, afewitems.py, in case you want to start
over with a prepopulated catalog.db


## Section 2 Requirements
I don't know how to check the version number of every package used in this
project.  Everything came preloaded within the Vagrant VM.

Here is a list of what is used according to pg_config.sh:
	apt-get -qqy update
	apt-get -qqy install postgresql python-psycopg2
	apt-get -qqy install python-sqlalchemy
	apt-get -qqy install python-pip
	pip install werkzeug==0.8.3
	pip install flask==0.9
	pip install Flask-Login==0.1.3
	pip install oauth2client
	pip install requests
	pip install httplib2
	pip install flask-seasurf


## Section 3 Installation
This is covered in the Setup Environment section


## Section 4 Set Up 
This is covered in the Setup Environment section


## Section 5 How to Run
This is covered in the Setup Environment section


## Section 6 Usage
When you invoke the app from localhost:8000 you will get a list of categories
and items.  You can click on any category to see the items stored in that
category.  You can click on any item to see a description.

Login with Google or Facebook to gain editing access.  Now you can create
categories or items.  If you own any items in the database, you can edit or
delete them.
