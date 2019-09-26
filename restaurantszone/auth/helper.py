from flask import session



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

    
def store_user_dict_to_session(user):
    session['facebook_id'] = user.get('facebook_id')
    session['access_token'] = user.get('access_token')
    session.permanent = True

def get_user_dict_from_session():
    return {
        'facebook_id': session.get('facebook_id'),
        'access_token': session.get('access_token')
    }

def delete_user_session():
    session.clear()