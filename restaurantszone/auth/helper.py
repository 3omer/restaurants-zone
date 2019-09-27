from flask import session, g, redirect, url_for
from functools import wraps


# def create_user(user):
#     '''
#     insert user record to databaase
#     '''
#     new_user = User(id=user.get('facebook_id'),
#                     name=user.get('name'),
#                     email=user.get('email'),
#                     picture=user.get('picture')
#                     )
#     session.add(new_user)
#     session.commit()

# decorator for views that required login
def loggin_required(view):
    @wraps(view)
    def decorated_func(*args, **kwargs):
        if g.user is None:
            flash('You are not authorized to perform this action .. please Login', category='warning')
            return redirect('/', 401)
        return view(*args, **kwargs)
    return decorated_func


def store_user_dict_to_session(user):
    session['facebook_id'] = user.get('facebook_id')
    session['picture'] = user.get('picture')
    session['access_token'] = user.get('access_token')
    session.permanent = True

def get_user_dict_from_session():
    return {
        'facebook_id': session.get('facebook_id'),
        'picture': session.get('picture'),
        'access_token': session.get('access_token'),
    }

def clear_session():
    session.clear()


def is_resource_owner(resource_owner_id):
    return g.get('user', None) and g.user.fb_id == resource_owner_id