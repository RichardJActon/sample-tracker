Development
===========

The [source code](https://github.com/RichardJActon/sample-tracker) is hosted on GitHub.

## Quickstart

```
git clone https://github.com/RichardJActon/sample-tracker.git

# Populate the .env file - see below

# get js & css dependencies
cd src/sample-tracker/static
npm ci
cd ../../../

docker compose up -d
```

The app will be served on [localhost:5080](http://localhost:5080)

This is an INSECURE DEVELOPMENT ONLY DEPLOYMENT with debug mode on and
a bind mount to the working directory so it will reflect your changes live.

## Tech Stack

### Secrets & Environment variables

A `.env` file needs to be defined which contains the following variables:

```
# These are used in the docker compose file which sets up MongoDb & Keycloak
MONGO_ROOT_USER=root
MONGO_ROOT_PWD=<SECRET>
MONGO_DATABASE=sampletracking

# These are used by both the docker compose and the app
APP_MONGO__PWD=<SECRET>
APP_MONGO__DATABASE=sampletracking
APP_MONGO__USER=appuser
APP_MONGO__AUTH_SOURCE="admin"
APP_OAUTH_ENDPOINTS__testing__client_secret=<SECRET>

# These are only for the app
APP_MONGO__HOST="127.0.0.1"
APP_MONGO__PORT="27018"
APP_SECRET_KEY=<SECRET>
```

`.env` is in the project `.gitignore` so that in the event that you populate
 it with any real credentials it is harder to accidentally commit them.

A `.envrc` file is also present for users of [direnv](https://direnv.net/), this will drop you
into the `uv` virtual environment and export the environment variables defined
in `.env` automatically when you `cd` into the project directory.

It is suggested that any secrets, such as the flask session secret, be defined
in `.env` and that this be sourced in the shell from which the app is launched.
This file should be managed with a secrets manager.

Alternatively these can be in defined with the rest of the application
configuration in `config.yaml` if the entire config is managed by your
secrets manager.
Environment variables will override config provided by this file so all
non-secret config can be specified here secrets made availabe through the
environment.

### Database & Authentication services

This application makes use of [MongoDb](https://www.mongodb.com/) as it's database backend.
It also makes use of a [Keycloak](https://www.keycloak.org/) server to handle authentication with OAuth2/OIDC.
Both of these can be made available in the development environment via Docker
There is a `docker-compose.yml` file in the project root directory which sets up
development instances of both of these services.

Run `docker compose up -d` to start these services and a development
deployment of the main application on [localhost:5080](http://localhost:5080).
This is for development ONLY it runs in debug mode and will live-update as
there is a bind mount to the project directory.
The app currently runs in a pre-built debian container from UV with a python
version selected to match the one in the `pyproject.toml` file.

DO NOT DEPLOY THIS TO PRODUCTION!!

This is not a secure configuration by default keycloak is running in dev mode,
the flask app is running with debug on and mongodb is exposed on the host
network by default so it is easy to connect with mongosh from the host for debugging.

The data for the database will be stored in `data/mongodb` which should be
emptied of everything but the .gitignore file it contains before first
starting the container for a clean empty database on container startup.

For additional details on setting up keycloak users for testing and development
see the comments in the docker compose file.

### Python

The primary framework used for the app is [Flask](https://flask.palletsprojects.com/en/stable/)
The [odmantic](https://art049.github.io/odmantic/) package is used to interface with the MongoDb database backend.

There is an application factory function defined in
`src/sample_tracker/__init__.py` and blueprints are also define in factory
functions called from within the primary app function.

The python environment for this project is managed with [uv](https://docs.astral.sh/uv/)

If you are not using the docker compose development environment and wish to
develop the app directly on your host providing your own mongoDB and OAuth/OIDC
endpoints here is how.

Dependencies can be installed run the sync command in the project root directory:

```
uv sync
```

The application can be started in debug mode with the following command:

```
uv run flask --debug --app src/sample_tracker run
```

This will run the app in the uv virtual environment without your first entering
that environment. To enter the virtual environment run:

```
source .venv/bin/activate
```

:::{tip}
This project contains a `.envrc` file if you have
[direnv](https://direnv.net/) and run `direnv allow` it will automatically drop
you into the python environment when you enter the directory so you don't
have to source the virtual env every time.
:::

System tools not in the uv environment:

- gnu make
  Used for building documenation
- mongosh
  Can be useful for degugging mongodb things from your development client### javascript

### java script & CSS

[npm](https://www.npmjs.com/) is used to manage the js dependencies of this project.
The `packages.json` and lock files can be found in the static assets directory:
`src/sample_tracker/static` 

To install the resources from npm run the following:

```
cd src/sample-tracker/static
npm ci
cd ../../../
```

Themeing is done with [Bootstrap](https://getbootstrap.com/)

### Documentation

The documentation is generated with [Sphinx](https://www.sphinx-doc.org/en/master/index.html).

### Conventions

When importing multiple things from a python module always use one import
per line and a trailing `,` e.g.:

```
from flask import (
    flask,
    current_app, # <-- note the trailing comma
)
```
Do not import multiple items on the same line, one per line make much better
git diffs and the trailing comma ensures the order does not change the diff
when the imports do not change.



