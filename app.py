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


@app.before_request
def load_logged_user():
    if login_session.get('facebook_id') is None:
        g.user = None
    else:
        g.user = get_user_dict_from_session()
        # is_owner returns True if the user is the owner of 
        # a restaurant or menu item given user_id as a parameter
        g.user['is_owner'] = lambda id: g.user['facebook_id'] == id or False 


# urls and handlers definitons
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    # TODO: sort options
    # sort_by: name, menu_length, 
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if g.user is None:
        flash('You are not authorized to perform this action .. please Login', category='warning')
        return redirect(url_for('showRestaurants'))

    form_handler = RestaurantFormHandler()
    if request.method == 'POST':
        form_handler = RestaurantFormHandler(**request.form)

        if form_handler.validate():
            valid_args = form_handler.input_arg
            new_restaurant = Restaurant(**valid_args, user_id=g.user['facebook_id'])
            session.add(new_restaurant)
            session.commit()
            flash(' restaurant %s is now available !' % new_restaurant.name, 'success')
            return redirect(url_for('showRestaurants'))
        else:
            return render_template('edit_restaurant.html', form=form_handler)
    return render_template('new_restaurant.html', form=form_handler)


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if g.user is None:
        flash('You are not authorized to perform this action .. please Login', category='warning')
        return redirect(url_for('showRestaurants'))

    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one_or_none()
    if restaurant.user_id != g.user.get('facebook_id'):
        flash('You dont have the permissions to perform this action.', category='danger')
        return redirect(url_for('showRestaurants'))
    if request.method == 'POST':
        new_name = request.form['name']
        form_handler = RestaurantFormHandler(name= new_name)
        if form_handler.validate():
            new_name = form_handler.input_arg['name']
            restaurant.name = new_name
            session.add(restaurant)
            session.commit()
            flash('changes saved !', 'success')
            return redirect(url_for('showRestaurants'))
        else:
            return render_template('edit_restaurants.html', form=form_handler)
    return render_template('edit_restaurant.html', form=form_handler)


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if g.user is None:
        flash('You are not authorized to perform this action .. please Login', category='warning')
        return redirect(url_for('showRestaurants'))
    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one_or_none()
    # menu_length = session.query(MenuItem).filter(MenuItem.restaurant == restaurant).count()
    if restaurant.user_id != g.user.get('facebook_id'):
        flash('You dont have the permissions to perform this action.', category='danger')
        return redirect(url_for('showRestaurants'))
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash('%s deleted' % restaurant.name, 'success')
        return redirect(url_for('showRestaurants'))
    return render_template('delete_restaurant.html', name=restaurant.name, menu_length=15)


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one_or_none()
    menu_items = session.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)
    return render_template('menu.html', restaurant=restaurant, menu_items=menu_items)


@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if g.user is None:
        flash('You are not authorized to perform this action .. please Login', category='warning')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
       
    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one_or_none()
    if g.user.get('facebook_id') != restaurant.user_id:
        flash("You don't have the permission to perform this action.", category="danger")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    form_handler = ItemFormHandler()
    if request.method == 'POST':
        # get data
        form_handler = ItemFormHandler(**request.form)
        form_is_valid = form_handler.validate()
        if form_is_valid:
            item_args = form_handler.input_args
            item = MenuItem(user_id=g.user['facebook_id'],restaurant_id=restaurant_id, **item_args)
            try:
                session.add(item)
                session.commit()
                flash('new menu item is added !', 'success')
            except Exception :
                flash("Couldn't save your changes.", category="warning")
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('edit_menu_item.html', form=form_handler)
    return render_template('new_menu_item.html', form=form_handler)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, item_id):
    if g.user is None:
        flash('You are not authorized to perform this action .. please Login', category='warning')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    item = session.query(MenuItem).filter(MenuItem.id == item_id).one_or_none()
    restaurant = session.query(Restaurant).filter(Restaurant.id ==  restaurant_id).one_or_none()
    if g.user.get('facebook_id') != item.user_id:
        flash("You don't have the permission to perform this action.", category="danger")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    
    if request.method == 'POST':
        # get data
        form_handler = ItemFormHandler(**request.form)
        if form_handler.validate():
            modified_args = form_handler.input_args
            item.name = modified_args['name']
            item.description = modified_args['description']
            item.course = modified_args['course']
            item.price = modified_args['price']
            try:
                session.add(item)
                session.commit()
            except Exception:
                flash('Couldn\'t save your changes.', category='warning')

            flash('menu item updated !', 'success')
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    return render_template('edit_menu_item.html', form=form_handler)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, item_id):
    if g.user is None:
        flash('You are not authorized to perform this action .. please Login', category='warning')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).one_or_none()
    item = session.query(MenuItem).filter(MenuItem.id == item_id).one_or_none()
    if g.user.get('facebook_id') != item.user_id:
        flash("You don't have the permission to perform this action.", category="danger")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    if request.method == 'POST':
        # delete menu item
        session.delete(item)
        session.commit()
        # flash user
        flash('menu item deleted !', 'success')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    return render_template('delete_menu_item.html', restaurant_name=restaurant['name'], item_name=item['name'])


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


@app.route('/auth/facebook', methods=['GET'])
def facebookAuth():
    # make sure to clean any previous login session
    # delete_user_from_session()
    facebook = FaceBookOauthSession()
    auth_url, state = facebook.authorization_url()
    login_session['state'] = state
    return redirect(auth_url)

@app.route('/auth/facebook/callback', methods=['GET'])
def facebookCallback():
    response_url = request.url
    facebook = FaceBookOauthSession(state=login_session['state'])
    token = facebook.fetch_token(authorization_response=response_url)
    profile = facebook.profile()
    profile['access_token'] = token.get('access_token')
    
    # get user from database  
    # if it doesnt exist create new user record
    user = session.query(User).filter(User.id == profile.get('facebook_id')).one_or_none()
    if user is None:
        create_user(profile)
        flash('Hey %s, account has been created for you' % profile.get('name'), category='success')
    else:
        flash('Welcome back %s' % user.name, category='success')

    store_user_dict_to_session(profile)
    return redirect(url_for('showRestaurants'))


@app.route('/auth/facebook/logout')
def facebookLogout():
    if g.user is None:
        flash('You are not logged in', category='info')
    else:
        delete_user_from_session()
        flash('You are logged out', category='info')
    return redirect(r'/')

@app.route('/auth/facebook/revoke')
def facebookRevoke():
    r = FaceBookOauthSession.authorized_session(g.user.get('access_token')).revoke()
    return r.json()


@app.route('/users', methods=['GET'])
def users():
    users = session.query(User).all()
    user = users[0]
    store_user_dict_to_session({'facebook_id':user.id, 'email': user.email, 'name': user.name, 'picture': user.picture})
    # app.logger.log(type(r.get('facebook_id')))
    return jsonify([user.serialize for user in users])



# helper functions
def create_user(user):
    '''
    insert user record to databaase
    '''
    new_user = User(id=user.get('facebook_id'),
                    name=user.get('name'),
                    email=user.get('email'),
                    picture=user.get('picture')
                    )
    session.add(new_user)
    session.commit()


def store_user_dict_to_session(user):

    login_session['facebook_id'] = user.get('facebook_id')
    login_session['username'] = user.get('name')
    login_session['email'] = user.get('email')
    login_session['picture'] = user.get('picture')
    login_session['access_token'] = user.get('access_token')
    login_session.permanent = True

def get_user_dict_from_session():
    return {
        'facebook_id': login_session.get('facebook_id'),
        'username': login_session.get('username'),
        'email': login_session.get('email'),
        'picture': login_session.get('picture'),
        'access_token': login_session.get('access_token')
    }

def delete_user_from_session():

    del login_session['facebook_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['access_token']


app.debug = True
app.run('0.0.0.0', 8000, use_debugger=True)
