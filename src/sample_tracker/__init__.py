#!/usr/bin/env python3
from flask import Flask
from sample_tracker import (
    index,
    login,
    project,
    pages,
    db,
    auth,
)
import os
import yaml
import logging
from pathlib import Path
from authlib.integrations.flask_client import OAuth
from pprint import pprint

def create_app():
    app = Flask(__name__, static_folder = "static", template_folder = "templates")


# Logging ----
    logging.basicConfig(
        format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# App Configuration ----
    config_path = "config.yaml"
    default_config_path_used = False
    try:
        config_path = os.environ["APP_CONFIG_PATH"]
    except:
        default_config_path_used = True

    # Read the main configuration
    app.config.from_file(
        Path().absolute() / config_path,
        load = lambda s: yaml.load(s, Loader = yaml.Loader)
    )
    # Read any environment variables which might overrule the config file
    # NB all env vars prefixed "APP_X" are available in app.config["X"]
    # For nested config env vars take the form: "APP_SUB__X" app.config["SUB"]["x"]
    app.config.from_prefixed_env(prefix="APP")
    
    if default_config_path_used:
        app.logger.info("APP_CONFIG_PATH not set using default path 'config.yaml'")

    try:
        if app.config["SECRET_KEY"] is None:
            raise Exception("Flask cookie secret not set!")
    except Exception as e:
        app.logger.error(str(e))

    # print complete config to log for debugging
    # app.logger.info(pprint(dict(app.config.items())))

# Authentication ----
    oauth = OAuth(app)
    auth.register_oauth_endpoints(oauth, app.config["OAUTH_ENDPOINTS"])
    oauth_endpoints = [*app.config["OAUTH_ENDPOINTS"]]

# Mongo DB connection ----

    # Connect to the database
    dbc = db.connect_to_database(app.config["MONGO"])
    engine = db.odmantic_sync_engine(app.config["MONGO"])

# Blueprint constructors ----
    app.register_blueprint(index.construct_bp(engine))
    app.register_blueprint(login.construct_bp(oauth, oauth_endpoints, engine))
    app.register_blueprint(project.construct_bp(engine))
    app.register_blueprint(pages.construct_bp(engine))
    
    return app

