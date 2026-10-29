# Sample Tracker

A web application for keeping track of the physical location of lab samples.

For additional information see the [Documentation](https://richardjacton.github.io/sample-tracker/).

## Development Quick start

Requires docker, uv, & npm

```
git clone https://github.com/RichardJActon/sample-tracker.git

# Populate the .env file - see below

# MongoDb & Keycloak
docker compose up -d

# python dependencies
uv sync
# (optional) direnv allow # automatically enter the python venv when in this directory

# js & css dependencies
cd src/sample-tracker/static
npm ci
cd ../../../

flask --debug --app src/sample_tracker run
```

**Secrets & Environment variables**

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

# Notes

login flow
- a user must first exist in an oauth/oidc provider.
- NB look into logout of all devices

roles
  - approver for restriction X
permissions
  - view
  - move
  - propose / edit
  - admin

viewer
  - no move, edit, group creation options visible

mover
  - can add events that update location
  - can create sample groups



database
- initial example user creation in the database init bash script
so not necessarily consistent with the content need be an initial object created
by the odmantic data model - consider a db init with python script run in the
docker setup

- add tag/commit hash version information as object metadata for all objects
to facilitate possible future database migrations to accomodate data model changes
