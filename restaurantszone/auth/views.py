from flask import ( Blueprint, url_for, redirect, session, request, flash, g )
from restaurantszone.auth.facebook_auth import FaceBookOauthSession
from restaurantszone.model import User
from .helper import store_user_dict_to_session, delete_user_session


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_request
def load_logged_user():
    if session.get('facebook_id') is None:
        g.user = None
    else:
        g.user = get_user_dict_from_session()
        # is_owner returns True if the user is the owner of 
        # a restaurant or menu item given user_id as a parameter
        g.user['is_owner'] = lambda id: g.user['facebook_id'] == id or False 


@bp.route('/facebook/login', methods=['GET'])
def facebookAuth():
    # make sure to clean any previous login session
    # delete_user_from_session()
    # TODO: logged in users shouldn't run this route
    # redirected to logout first

    facebook = FaceBookOauthSession()
    auth_url, state = facebook.authorization_url()
    session['state'] = state
    return redirect(auth_url)


@bp.route('/facebook/callback', methods=['GET'])
def facebookCallback():
    response_url = request.url
    facebook = FaceBookOauthSession(state=session['state'])
    token = facebook.fetch_token(authorization_response=response_url)
    profile = facebook.profile()
    profile['access_token'] = token.get('access_token')
    
    # get user from database  
    # if it doesnt exist create new user record
    user = User.get_by_id(session['facebook_id'])
    if user is None:
        user = User(
            profile['name'], 
            profile['email'], 
            profile['facebook_id'], 
            profile['picture']
            )
        user.save()
        flash('Hey %s, an account has been created for you' % profile.get('name'), category='success')
    else:
        flash('Welcome back %s' % user.name, category='success')

    store_user_dict_to_session(profile)
    return redirect(url_for('showRestaurants'))


@bp.route('/auth/facebook/logout')
def facebookLogout():
    if g.user is None:
        flash('You are not logged in', category='info')
    else:
        delete_user_session()
        flash('You are logged out', category='info')
    return redirect(url_for('showRestaurants'))

@bp.route('/auth/facebook/revoke')
def facebookRevoke():
    r = FaceBookOauthSession.authorized_session(g.user.get('access_token')).revoke()
    return r.json()





