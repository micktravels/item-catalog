from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask.ext.seasurf import SeaSurf
from sqlalchemy import create_engine, asc, desc, func, distinct
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
csrf = SeaSurf(app)
csrf.init_app(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



############### BEGIN LOGIN CODE SECTION ################

# Create anti-forgery state token.  Since the Login page is now a modal that's part of every screen,
# this STATE gets regenerated on every page whenever you aren't logged in
def generateState():
    # only update a random STATE if we aren't already logged in
    if 'email' not in login_session:
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
        login_session['state'] = state
    return login_session['state']

# This function connects with Facebook.  It's called from the login.html page after a user enters username and password
# It was almost entirely borrowed from the class lesson
@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # print "DEBUG: fbconnect:  initiated"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists in the database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

# Disconnect from facebook.  Called from the disconnect function
@csrf.exempt
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Connect to google.  This function was almost entirely borrowed from the class project
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token, that 32-character random string thingy
    # print "STATE = " + request.args.get('state')
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    if login_session['username']:
        output += login_session['username'] + '!</h1>'
        flash("you are now logged in as %s" % login_session['username'])
    else:
        output += login_session['email'] + '</h1>'
        flash("you are now logged in as %s" % login_session['email'])
    output += '<img src="' + login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output

# Disconnect from google.  This function is called by the disconnect function.
@csrf.exempt
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider.  Called when user clicks the Logout link
@csrf.exempt
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLatest'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showLatest'))

############## END LOGIN CODE SECTION ####################


############## BEGIN ENDPOINT SECTION ####################

# Full nested JSON dump of database
@app.route('/JSON/')
def dumpJSON():
    categories = session.query(Category).all()
    categoryList = []
    for c in categories:
        cdict = {}
        cdict['id'] = c.id
        cdict['name'] = c.name
        items = session.query(Item).filter(Item.category_id==c.id).all()
        itemList = []
        for i in items:
            idict = {}
            idict['id'] = i.id
            idict['name'] = i.name
            idict['description'] = i.description
            idict['imgURL'] = i.imgURL
            itemList.append(idict)
        # now we have a list of item dictionaries to add to the category dictionary
        cdict['items'] = itemList
        # and let's add the category dictionary to the full list of categories
        categoryList.append(cdict)
    jsonDict = {'Categories': categoryList}
    return jsonify(jsonDict)

# Full nested XML dump of the database.  Done using a template
@app.route('/XML/')
def dumpXML():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('items.xml', categories=categories, items=items)

################# END ENDPOINT CODE SECTION #####################



################# BEGIN CATALOG PROCESSING SECTION ####################

# Home screen shows all categories and the latest items, which in turn have their categories tagged
@app.route('/', methods=['GET', 'POST'])
@app.route('/category/', methods=['GET', 'POST'])
def showLatest():
    state = generateState()
    categories = session.query(Category).order_by(asc(Category.name))
    latestItems = session.query(Item, Category).filter(Item.category_id==Category.id)
    latestItems = latestItems.order_by(asc(Item.addDate)).limit(7)
    if request.method == 'POST':
        formtype = request.form['formtype']
        # print "Processing Form of type " + formtype
        if formtype == 'newitem':
            newItem('showLatest')
        if formtype == 'newcategory':
            newCategory('showLatest')
    # fallthrough to just rerendering homepage - just in case
    return render_template('index.html', categories=categories, items=latestItems, STATE=state)


# Create a new category
# @app.route('/category/new/', methods=['GET', 'POST'])
def newCategory(camefrom):
    # print "DEBUG: entered newCategory() from " + camefrom
    if 'email' not in login_session:
        return redirect('/')
    else:
        newCategory = Category(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        newCategory = session.query(Category).filter(Category.name==request.form['name']).one()
        # print "DEBUG newCategory:  category_id = " + str(newCategory.id) + ", camefrom = " + camefrom
        if camefrom == 'showItems':
            return newCategory.id
        else:
            return

# Show a category item


@app.route('/category/<int:category_id>/', methods=['GET', 'POST'])
def showItems(category_id):
    state = generateState()
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).filter_by(category_id=category_id).all()
    if request.method == 'POST':
        formtype = request.form['formtype']
        # print "DEBUG showItems: Processing Form of type " + formtype
        if formtype == 'newitem':
            newItem('showItems')
        if formtype == 'newcategory':
            category_id = newCategory('showItems')
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).filter_by(category_id=category_id).all()
    # print "DEBUG: back to showItems routine, ready to rerender"
    return render_template('showitems.html', items=items, category=category, categories=categories, STATE=state)

# Create a new item item
# implementing this as a modal, so a separate web address is not necessary to access.
# function gets called from showLatest or showItems
# @app.route('/category/item/new/', methods=['GET', 'POST'])
def newItem(camefrom):
    # print "DEBUG: newItem() entered from " + camefrom
    if 'email' not in login_session:
        return redirect('/')
    else:
        newItem = Item(name=request.form['name'], description=request.form[
                            'description'], imgURL=request.form['imgURL'],
                            category_id=request.form['category_id'], user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Items %s Item Successfully Created' % (newItem.name))
        return

#showItemDescription repurposes the entire screen for a single item.
# buttons exist on the bottom of the screen to EDIT, DELETE, or go back, depending if you are logged in or not
# EDIT and DELETE buttons are simple forms with a single hidden attribute
@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def showItemDescription(item_id):
    categories = session.query(Category).order_by(asc(Category.name))
    item = session.query(Item).filter_by(id=item_id).one()
    # print "DEBUG showItemDescription"
    creator = getUserInfo(item.user_id)
    # POST will come from an editItem or deleteItem modal
    if request.method == 'POST':
        formtype = request.form['formtype']
        # print "DEBUG showItemDescription: Processing Form of type " + formtype
        if formtype == 'edititem':
            editItem(item_id)
        if formtype == 'deleteitem':
            deleteItem(item_id)
            return redirect(url_for('showLatest'))
    return render_template('showitemdescription.html', item=item, creator=creator, categories=categories)

# Edit an existing item
# implementing this as a modal, so a separate web address is not necessary to access.
# function gets called from showItemDescription modal which already processed the POST and brought us here
# @app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if 'email' not in login_session:
        # we should never get here, but just in case...
        return redirect('/')
    if request.form['name']:
        editedItem.name = request.form['name']
    if request.form['description']:
        editedItem.description = request.form['description']
    if request.form['imgURL']:
        editedItem.imgURL = request.form['imgURL']
    if request.form['category_id']:
        editedItem.category_id = request.form['category_id']
    session.add(editedItem)
    session.commit()
    flash('Item Successfully Edited')
    return


# Delete a item item
# implementing this as a modal, so a separate web address is not necessary to access.
# function gets called from showItemDescription modal which already processed the POST and brought us here
# @app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if 'email' not in login_session:
        # we shouldn't ever get here, but just in case...
        return redirect('/login')
    session.delete(itemToDelete)
    session.commit()
    flash('Item Successfully Deleted')
    return

################## END CATALOG PROCESSING SECTION ###################


################## MISC HELPFUL FUNCTIONS ###################

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

################### END MISC HELPFUL FUNCTIONS ###################

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)