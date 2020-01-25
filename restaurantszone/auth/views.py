from flask import ( Blueprint, url_for, redirect, session, request, flash, g )
from restaurantszone.auth.facebook_auth import FaceBookOauthSession
from restaurantszone.model import User
from .helper import store_user_dict_to_session, loggin_required


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_user():
    if session.get('facebook_id') is None:
        g.user = None
    else:
        g.user = User.get_by_id(session['facebook_id'])
        # accessed from templates, return true if current user is owner of a resource
        g.is_owner = lambda id: id == g.user.fb_id


@bp.route('/facebook/login', methods=['GET'])
def facebookAuth():
    flash('Sorry.Facebook Log in is not available now!', category='info')
    return redirect('/')
    # make sure to clean any previous login session
    # delete_user_from_session()
    # logged in users shouldn't run this route
    if g.user is not None:
        flash('You are already logged in as {}.'.format(g.user.name), category='info')
        return redirect('/')
    session.pop('facebook_id', None)
    facebook = FaceBookOauthSession()
    auth_url, state = facebook.authorization_url()
    session['state'] = state
    return redirect(auth_url)


@bp.route('/facebook/callback', methods=['GET'])
def facebookCallback():
    response_url = request.url
    facebook = FaceBookOauthSession(state=session['state'])
    token = facebook.fetch_token(authorization_response=response_url)
    res = facebook.user_info()
    if 'error' in res:
        flash(res['error'], category='danger')
        return redirect(url_for('restaurant.showRestaurant'))
    # get user from database  
    # if it doesnt exist create new user record
    user = User.get_by_id(res.get('facebook_id'))
    if user is None:
        user = User(
            res['name'], 
            res['email'], 
            res['facebook_id'], 
            res['picture']
            )
        user.save()
        flash('Hey %s, an account has been created for you' % res.get('name'), category='success')
    else:
        flash('Welcome back %s' % user.name, category='success')

    store_user_dict_to_session(res)
    return redirect(url_for('restaurant.showRestaurants'))


@bp.route('/facebook/logout')
@loggin_required
def facebookLogout():
    session.clear()
    flash('You are now logged out.', category='info')
    return redirect(url_for('restaurant.showRestaurants'))

@bp.route('/facebook/revoke')
@loggin_required
def facebookRevoke():
    r = FaceBookOauthSession.authorized_session(session.get('access_token')).revoke()
    return r.json()


@bp.route('/test/login')
def test_login():
    user = {}
    user['facebook_id'] = 123456
    user['picture'] = 'https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png'
    user['access_token'] = 'test'
    store_user_dict_to_session(user)
    user = g.get('user', None)
    return(session['facebook_id'])