from flask import Flask,request, render_template, url_for, redirect,flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import fakeDB

app = Flask(__name__)

# database configuration
engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# urls and handlers definitons
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = fakeDB.get_all_restaurants()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        new_name = request.form['name']
        fakeDB.create_restaurant(new_name)
        flash(' restaurant %s is created !' % new_name)
        return redirect(url_for('showRestaurants'))
    return render_template('new_restaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = fakeDB.get_restaurant(restaurant_id)
    if request.method == 'POST':
        new_name = request.form['name']
        fakeDB.update_restaurant(restaurant_id, new_name)
        flash('change saved !')
        return redirect(url_for('showRestaurants'))
    return render_template('edit_restaurant.html', name=restaurant.get('name'))


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = fakeDB.get_restaurant(restaurant_id)
    menu_length = 15
    if request.method == 'POST':
        fakeDB.delete_restaurant(restaurant_id)
        flash('%s deleted' % restaurant['name'])
        return redirect(url_for('showRestaurants'))
    return render_template('delete_restaurant.html', name=restaurant['name'], menu_length=menu_length)


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    restaurant = fakeDB.restaurant
    menu_items = fakeDB.items
    return render_template('menu.html', name=restaurant['name'], menu_items=menu_items )


@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        # validate input
        # insert data
        # flash a message
        flash('new menu item is added !')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    return render_template('new_menu_item.html')


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, item_id):
    item = fakeDB.item
    if request.method == 'POST':
        #validate input
        #update item
        # flash
        flash('menu item updated !')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    return render_template('edit_menu_item.html', item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, item_id):
    item = fakeDB.item
    restaurant = fakeDB.restaurant
    if request.method == 'POST':
        # delete menu item
        # flash user
        flash('menu item deleted !')
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    return render_template('delete_menu_item.html', restaurant_name=restaurant['name'], item_name=item['name'])


app.secret_key = 'ulvuelhk'