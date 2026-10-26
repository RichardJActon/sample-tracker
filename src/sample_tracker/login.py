# Login ----
from flask import (
    Blueprint,
    render_template,
    make_response,
    current_app,
    redirect,
    url_for,
    session,
)

# from pims.session import *
# from pims.utility import jsonify

from datetime import(
    datetime,
    timezone,
)
import time
from sample_tracker.auth import revoke_current_session_token
from sample_tracker.datamodel import Person
from odmantic import query

# ips,
def construct_bp(oauth, oauth_providers, engine):
    bp = Blueprint('login', __name__) 
    
    @bp.route('/login')
    def login():
        return render_template("pages/login.html", oauth_providers = oauth_providers)

    @bp.route('/oauth_login/<oauth_provider>')
    def oauth_login(oauth_provider):
        redirect_uri = url_for('login.authorize', oauth_provider = oauth_provider, _external=True)
        return oauth.__getattr__(oauth_provider).authorize_redirect(redirect_uri)

    @bp.route('/authorize/<oauth_provider>')
    def authorize(oauth_provider):
        token = oauth.__getattr__(oauth_provider).authorize_access_token()
        userinfo = token.get('userinfo')
        current_app.logger.info(
            "User: " + userinfo.get('preferred_username') +
            " attempted to log in at: "+ datetime.now(tz = timezone.utc).strftime('%Y-%m-%d %H:%M:%S') +
            ", Last authorised at: " +
            datetime.fromtimestamp(userinfo.get('auth_time')).strftime('%Y-%m-%d %H:%M:%S')
        )
        # resp = oauth.testing.get('user')
        # resp.raise_for_status()
        # profile = resp.json()

        person = engine.find_one(Person, Person.username == userinfo["preferred_username"])
        try:
            if person is None:
                person = Person(
                    given_name = userinfo["given_name"],
                    family_name = userinfo["family_name"],
                    username = userinfo["preferred_username"],
                    email = userinfo["email"],
                    email_verified = bool(userinfo.get("email_verified") or False),
                    last_authenticated = datetime.fromtimestamp(userinfo.get("auth_time"), tz = timezone.utc),
                )
                # person = engine.find_one(Person, Person.username == userinfo["preferred_username"])
                raise Exception(
                    f"Person not found in database, created new Person: {userinfo['preferred_username']}"
                )
        except Exception as e:
            current_app.logger.info(e)

        try:
            if bool(person.disabled or False):
                raise Exception(f"Account disabled for {person.username}!")
            else:
                session["user"] = userinfo
                session["id_token"] = token.get("id_token")
                session["oauth_provider"] = oauth_provider
        except Exception as e:
            current_app.logger.info(str(e))
        
        return redirect('/')

    # debugging user info
    # @bp.route("/profile")
    # def profile():
    #     userinfo = session.get("user")
    #     return f"<p>{str(userinfo)}</p>"

    @bp.route("/logout")
    def logout():
        id_token = session.pop("id_token", None)
        redirect_uri = url_for('login.logged_out', _external=True)
        revoke_current_session_token(current_app, oauth)
        return oauth.__getattr__(session.get("oauth_provider")).logout_redirect(
            post_logout_redirect_uri = redirect_uri,
            id_token_hint = id_token
        )

    @bp.route('/logged_out')
    def logged_out():
        state_data = oauth.__getattr__(session["oauth_provider"]).validate_logout_response()
        # state_data just contains the re-direct URL to this page
        session.pop("user", None)
        return render_template("pages/logout_confirmation.html")

    return bp
