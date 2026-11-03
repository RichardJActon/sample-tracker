# Pages ---- 
from sample_tracker.datamodel import (
    Person,
)
from sample_tracker.auth import requires_auth
from sample_tracker.permissions import (
    get_current_person, # session?
)
from sample_tracker.utility import get_form
from flask import (
    Flask,
    Blueprint,
    render_template,
    session,
    current_app,
)
def construct_bp(engine):
    bp = Blueprint("pages", __name__)
    @bp.route("/account")
    @requires_auth
    def account():
        try:
            person = get_current_person(engine, session)
        except Exception as e:
            current_app.logger.exception("User not found" + str(e))
        
        try:
            n_projects = engine.count(Project, Project.owner == person.id)
        except Exception as e:
            n_projects = 0
            current_app.logger.info(e)
            
        return render_template(
            "pages/account.html",
            person = person,
            n_projects = n_projects
        )
        # pass


    return bp
