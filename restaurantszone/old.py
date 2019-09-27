import os
from flask import Flask,request, render_template, url_for, redirect,flash, jsonify, g
from flask import session as login_session
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from forms_handler import ItemFormHandler, RestaurantFormHandler
app = Flask(__name__)
app.secret_key = 'ulvuelhk'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

# database configuration
engine = create_engine('sqlite:///restaurantmenu-v2.0.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()




# urls and handlers definitons




#####
# here goes the api methods
# even though its really bad structure
# so I should seprate the code TODO
####
@app.route('/restaurants/JSON')
def restaurantJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    return jsonify(MenuItems=[item.serialize for item in menu_items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/JSON')
def menuItemJSON(restaurant_id, item_id):
    item = session.query(MenuItem)\
                .filter(and_(MenuItem.id == item_id, MenuItem.restaurant_id == restaurant_id))\
                .one_or_none()
    return jsonify(MenuItem=item.serialize if item else {})


####
# TODO : 
# use one query when possible etc : 
# item = session.query(MenuItem).filter(and_(MenuItem.id == id, Restaurant.id == id)).one_or_none()
# or :
# session.query(MenuItem).with_parent(restaurant, 'restaurant_id')
# theres is more check the docs
####

# Here goes the authorization routes 
import facebook_credintials
from facebook_oauth import FaceBookOauthSession





@app.route('/users', methods=['GET'])
def users():
    users = session.query(User).all()
    user = users[0]
    store_user_dict_to_session({'facebook_id':user.id, 'email': user.email, 'name': user.name, 'picture': user.picture})
    # app.logger.log(type(r.get('facebook_id')))
    return jsonify([user.serialize for user in users])



# helper functions





app.debug = True
app.run('0.0.0.0', 8000, use_debugger=True)
