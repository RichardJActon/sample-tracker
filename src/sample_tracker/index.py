# Index ----
from sample_tracker.permissions import can_person_create_project
from sample_tracker.auth import requires_auth
from sample_tracker.datamodel import (
    Project,
    Person
)
from flask import (
    Blueprint,
    render_template,
    session,
    current_app
) 
from odmantic import query

def construct_bp(engine):
    bp = Blueprint('index', __name__)

    @bp.route("/")
    @requires_auth
    def index():
        person = engine.find_one(
            Person, Person.username == session["user"]["preferred_username"]
        )
        # Get recent projects
        try:
            recent_projects = list(engine.find(
                Project, Project.owner == person.id,
                sort = query.desc(Project.date_created), limit = 10
            ))
        except Exception as e:
            recent_projects = []
            current_app.logger.exception(e)
            
        can_create_projects = can_person_create_project(person)
        
        return render_template(
            "pages/index.html",
            person = person, can_create_projects = can_create_projects,
            projects = recent_projects
        )
    return bp
