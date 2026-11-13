# Index ----
from sample_tracker.permissions import (
    get_current_person,
)
from sample_tracker.auth import requires_auth
from sample_tracker.datamodel import (
    Project,
    Person,
)
from flask import (
    Blueprint,
    render_template,
    session,
    current_app,
) 
from odmantic import (
    query,
)
from odmantic.query import QueryExpression

def construct_bp(engine):
    bp = Blueprint('index', __name__)

    @bp.route("/")
    @requires_auth
    def index():
        person = get_current_person(engine, session)
        # Get recent projects (owned or member)
        try:
            recent_projects = list(engine.find(
                Project, query.or_(
                    Project.owner == person.id,
                    QueryExpression({
                        f"authorizations.{str(person.id)}": {"$exists" : True}
                    })
                ),
                sort = query.desc(Project.date_created), limit = 10
            ))
        except Exception as e:
            recent_projects = []
            current_app.logger.exception(e)
        
        return render_template(
            "pages/index.html",
            person = person, projects = recent_projects
        )
    return bp
