from flask import ( Blueprint, render_template, url_for, redirect, session, request, flash, g )
from restaurantszone.model import User, Restaurant
from .auth.helper import loggin_required
from .forms_handler import RestaurantFormHandler



tem_prefix = '/restaurant/'
bp = Blueprint('restaurant', __name__)

redirect_url = '/restaurants'

@bp.route('/')
@bp.route('/restaurants')
def showRestaurants():
    # TODO: sort options
    # sort_by: name, menu_length, 
    restaurants = Restaurant.get_all()
    return render_template(tem_prefix + 'restaurants.html', restaurants=restaurants)


@bp.route('/new', methods=['GET', 'POST'])
@loggin_required
def newRestaurant():
    form_handler = RestaurantFormHandler()
    if request.method == 'POST':
        form_handler = RestaurantFormHandler(
            name=request.form['name']
        )

        if form_handler.validate():
            valid_args = form_handler.input_arg
            new_restaurant = Restaurant(**valid_args, user_id=g.user.fb_id)
            new_restaurant.save()
            flash(' restaurant %s is now available !' % new_restaurant.name, 'success')
            return redirect(url_for('.showRestaurants'))
       
        else:
            return render_template(tem_prefix + 'edit_restaurant.html', form=form_handler)
    return render_template(tem_prefix + 'new_restaurant.html', form=form_handler)

@loggin_required
@bp.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    restaurant = Restaurant.get_by_id(restaurant_id)
    if restaurant is None:
        flash('Entry not Found, it might have been deleted.', category='danger')
        return redirect(redirect_url)
    
    elif restaurant.user_id != g.user.fb_id:
        # TODOL use g.user.is_owner('item_id)
        flash('You dont have the permissions to perform this action.', category='danger')
        return redirect(url_for('.showRestaurants'))
    form_handler = RestaurantFormHandler(restaurant.name)
    if request.method == 'POST':
        new_name = request.form['name']
        form_handler = RestaurantFormHandler(name= new_name)
        if form_handler.validate():
            new_name = form_handler.input_arg['name']
            restaurant.name = new_name
            restaurant.save()
            flash('changes are saved.', 'success')
            return redirect(redirect_url)
    return render_template(tem_prefix + 'edit_restaurant.html', form=form_handler)


@bp.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
@loggin_required
def deleteRestaurant(restaurant_id):
    restaurant = Restaurant.get_by_id(restaurant_id)
    #TODO: menu_length = session.query(MenuItem).filter(MenuItem.restaurant == restaurant).count()
    if restaurant is None:
        flash('Entry not Found, it might have been deleted.', category='danger')
        return redirect(redirect_url)
    
    elif restaurant.user_id != g.user.fb_id:
        flash('You dont have the permissions to perform this action.', category='danger')
        return redirect(redirect_url)
    
    if request.method == 'POST':
        restaurant.delete()
        flash('%s deleted' % restaurant.name, 'success')
        return redirect(redirect_url)
    return render_template(tem_prefix + 'delete_restaurant.html', name=restaurant.name, menu_length=15)
