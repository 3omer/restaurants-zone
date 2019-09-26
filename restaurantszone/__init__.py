import os
from flask import Flask
from . import db

from restaurantszone.auth import views

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'restaurantsmenu.db'), 
    )

    if test_config is None:
        # load instance configs
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError as identifier:
        pass


    db.init_app(app)
    
    # register blueprints
    app.register_blueprint(views.bp)


    @app.route('/hello')
    def hello():
        return 'hello'
    return app