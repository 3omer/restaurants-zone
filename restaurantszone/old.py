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
