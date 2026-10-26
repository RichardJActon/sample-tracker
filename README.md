# Sample Tracker

A web application for keeping track of the physical location of lab samples.

## Development

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

# These are only for the app
APP_MONGO__HOST="127.0.0.1"
APP_MONGO__PORT="27018"
APP_SECRET_KEY=<SECRET>
```

`.env` is in the project `.gitignore` so that in the event that you populate
 it with any real credentials it is harder to accidentally commit them.

A `.envrc` file is also present for users of [direnv](), this will drop you
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

This application makes use of MongoDb as it's database backend.
It also makes use of a Keycloak server to handle authentication with OAuth2/OIDC.
Both of these can be made available in the development environment via Docker
There is a docker-compose.yml file in the project root directory which sets up
development instances of both of these services.

Run `docker compose up -d` to start these services

The data for the database will be stored in `data/mongodb` which should be
emptied of everything but the .gitignore file it contains before first
starting the container

### Python

The python environment for this project is managed with [uv]()

The primary framework used for the app is [Flask]()
The [odmantic]() package is used to interface with the MongoDb database backend.

There is an application factory function defined in
`src/sample_tracker/__init__.py` and blueprints are also define in factory
functions called from within the primary app function.

The application can be started in debug mode with the following command:

```
flask --debug --app src/sample_tracker run
```

### javascript

[npm]() is used to manage the js dependencies of this project.
The `packages.json` and lock files can be found in the static assets directory:
`src/sample_tracker/static` 

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
