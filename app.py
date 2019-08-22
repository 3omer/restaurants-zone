from flask import Flask,request, render_template, url_for, redirect,flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

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
    return 'This page shows all restaurants'


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    return 'this page is a form for new adding restaurant'


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    return 'This page is a form to edit restaurant %s' % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    return 'This page is for deleting restaurant %s' % restaurant_id


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    return 'this page shows restuarant %s menu' % restaurant_id


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/new')
def newMenuItem(restaurant_id, item_id):
    return 'this page is to create new menu item %s' % item_id


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/edit')
def editMenuItem(restaurant_id, item_id):
    return 'this page is for editing restaurant menu item %s' % item_id


@app.route('/restaurant/<int:restaurant_id>/menu/<int:item_id>/delete')
def deleteMenuItem(restaurant_id, item_id):
    return 'this page is for deleting menu item %s' % item_id