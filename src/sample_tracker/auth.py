# auth
from flask import (
    session,
    url_for,
    redirect,
)
from functools import wraps
from typing import (
    Any,
)
from authlib.integrations.flask_client import OAuth
from authlib.integrations.requests_client import OAuth2Session
from sample_tracker.datamodel import (
    Person,
    Project,
)

def register_oauth_endpoints(oauth: OAuth, endpoints: dict[str, Any]) -> None:
    """
    Note that the `openid` scope is expected to be requested and the useinfo
    within it is expected to be present in the token.
    """
    for k,v in endpoints.items():
        oauth.register(k, **v)

def revoke_current_session_token(app, oauth):
    provider = session.get('oauth_provider')
    
    client = OAuth2Session(
        oauth.__getattr__(provider).client_id,
        oauth.__getattr__(provider).client_secret,
        scope= oauth.__getattr__(provider).client_kwargs['scope']
    )
    
    client.revoke_token(
        # NB this require the revokation endpoint to be explicitly set in the OAuth provider config
        url = app.config['OAUTH_ENDPOINTS'].get(provider).get('revocation'),
        token = session.get("id_token") # ['token']['access_token']
    )

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated

# def can_person_see_project(person: Person, project: Project) -> bool:
#     # if person["is_admin"]:
#     if person.is_admin:
#         return True

#     # if person["_id"] == project["owner"]:
#     if person.id == project.owner:
#         return True

#     # We'll do some checking for sharing eventually.

#     return False

# def can_person_edit_project(person: Person, project: Project) -> bool:
#     if person.is_admin:
#         return True

#     if person.id == project.owner:
#         return True

#     return False
