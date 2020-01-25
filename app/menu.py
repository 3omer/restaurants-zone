from flask import ( Blueprint, render_template, url_for, redirect, session, request, flash, g )
from app.model import User, MenuItem, Restaurant
from app.auth.helper import loggin_required, is_resource_owner
from app.forms_handler import ItemFormHandler

temp_prefix = '/menu/'

bp = Blueprint('menu', __name__, url_prefix='/restaurant')

@bp.route('/<int:restaurant_id>')
@bp.route('/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    restaurant = Restaurant.get_by_id(restaurant_id)
    if restaurant:
        menu_items = MenuItem.get_restaurant_menu(restaurant_id)
    return render_template(temp_prefix + 'menu.html', restaurant=restaurant, menu_items=menu_items)

@loggin_required
@bp.route('/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = Restaurant.get_by_id(restaurant_id)
    if restaurant is None:
        flash('Restaurant not found.', category='danger')
        return redirect('restaurant.showRestaurants')
    elif not is_resource_owner(restaurant.user_id):
        flash("You don't have the permission to perform this action.", category="danger")
        return redirect(url_for('menu.restaurantMenu', restaurant_id=restaurant_id))
    
    form_handler = ItemFormHandler()
    if request.method == 'POST':
        # get data
        form_handler = ItemFormHandler(
            name=request.form['name'],
            course=request.form['course'],
            description=request.form['description'],
            price=request.form['price'],
            user_id=g.user.fb_id,
            restaurant=restaurant
        )

        form_is_valid = form_handler.validate()
        if form_is_valid:
            item_args = form_handler.input_args
            item = MenuItem(user_id=g.user.fb_id, restaurant_id=restaurant_id, **item_args)
            item.save()
            return redirect(url_for('menu.restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template(temp_prefix + 'edit_menu_item.html', form=form_handler)
    return render_template(temp_prefix + 'new_menu_item.html', form=form_handler)

@loggin_required
@bp.route('/<int:restaurant_id>/menu/<int:item_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, item_id):
    item = MenuItem.get_by_id(item_id)
    if not ( item and item.restaurant_id == restaurant_id ):
        flash('Item not found.', category='danger')
        return redirect(url_for('.restaurantMenu', restaurant_id=restaurant_id))

    if not is_resource_owner(item.user_id):
        flash("You don't have the permission to perform this action.", category="danger")
        return redirect(url_for('.restaurantMenu', restaurant_id=restaurant_id))
    form_handler = ItemFormHandler(name=item.name, description=item.description, course=item.course, price=item.price)
    if request.method == 'POST':
        # get data
        form_handler = ItemFormHandler(
            name=request.form['name'],
            course=request.form['course'],
            description=request.form['description'],
            price=request.form['price'],
            user_id=g.user.fb_id
        )

        if form_handler.validate():
            modified_args = form_handler.input_args
            item.name = modified_args['name']
            item.description = modified_args['description']
            item.course = modified_args['course']
            item.price = modified_args['price']
            item.save()
            flash('menu item updated.', 'success')
            return redirect(url_for('menu.restaurantMenu', restaurant_id=restaurant_id))
    return render_template(temp_prefix + 'edit_menu_item.html', form=form_handler)

@loggin_required
@bp.route('/<int:restaurant_id>/menu/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, item_id):
    item = MenuItem.get_by_id(item_id)
    if not (item and item.restaurant_id == restaurant_id):
        flash('Item not found.', category='danger')
        return redirect(url_for('menu.restaurantMenu', restaurant_id=restaurant_id))
    elif not is_resource_owner(item.user_id):
        flash("You don't have the permission to perform this action.", category="danger")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    if request.method == 'POST':
        # delete menu item
        item.delete()
        # flash user
        flash('menu item deleted.', 'success')
        return redirect(url_for('.restaurantMenu', restaurant_id=restaurant_id))
    return render_template(temp_prefix + 'delete_menu_item.html', restaurant_name=item.restaurant.name, item_name=item.name)