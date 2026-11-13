from sample_tracker.auth import (
    requires_auth,
)
from sample_tracker.permissions import (
    get_current_person,
)
from sample_tracker.datamodel import (
    Restriction,
    Project, ApprovalStatus,
)
from flask import (
    Blueprint,
    session,
    Response, current_app, render_template,
)
from odmantic import query

def construct_bp(engine):
    bp = Blueprint("approval", __name__)

    @bp.route("/approvals")
    @requires_auth
    def approvals():
        person = get_current_person(engine, session)
        person_roles = {r.value for r in person.roles}
        restrictions = {r.value for r in Restriction}
        approver_roles_held = person_roles & restrictions
        try:
            if "Admin" not in person_roles and approver_roles_held == {}:
                m = "Only admins and restriction approvers can interact with the approvals page"
                raise PermissionError(m)
        except Exception as e:
            current_app.logger.exception(e)
            return Response(str(e), status="403")

        # query cannot be run with odmantic find interface drop to raw pymongo
        # then reconstruct odmantic objects from raw result
        projects = engine.get_collection(Project)
        relevant_projects = {}
        for role in approver_roles_held:
            relevant_projects[role] = [
                Project.model_validate_doc(doc) for doc in
                # project with restrictions for which you are an approver
                projects.find({
                    "$expr": {"$in": [role, "$restrictions"]}
                }).to_list()
            ]
        
        return render_template(
            "pages/approvals.html",
            relevant_projects = relevant_projects,
            person = person,
            approval_status = ApprovalStatus
        )

    return bp
