from bson import ObjectId
from sample_tracker.utility import get_form
# import requests
from sample_tracker.auth import (
    requires_auth,
)
from sample_tracker.permissions import (
    get_current_person, can_person_edit_project,
)
from sample_tracker.datamodel import (
    Restriction,
    Project,
    ApprovalStatus,
)
from flask import (
    Blueprint,
    session,
    Response,
    current_app,
    render_template,
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

    @bp.route("/approval_requests", methods = ["GET", "POST"])
    @requires_auth
    def approval_requests():
        person = get_current_person(engine, session)
        form = get_form() # request.form.to_dict()
        try:
            project = engine.find_one(Project, Project.id == ObjectId(form["project_id"]))
        except Exception as e:
            current_app.logger.exception(str(e))

        restriction = form["restriction"]
        current_status = ApprovalStatus(project.restriction_details[restriction]["status"])
        target_status = ApprovalStatus(form["status"])

        if person.is_admin():
            # allows movements bettween states that would not normally be permitted
            # e.g. directly from not submitted to approved
            project.restriction_details[restriction]["status"] = target_status.value
            engine.save(project)
            return "OK"
        
        try:
            if can_person_edit_project(person, project):
                if current_status in ApprovalStatus.submitter_sources() and target_status in ApprovalStatus.submitter_targets():
                    project.restriction_details[restriction]["status"] = target_status.value
                    engine.save(project)
                    
                elif current_status in ApprovalStatus.approver_sources() and target_status in ApprovalStatus.approver_targets():
                    if Role(restriction) in person.roles:
                        project.restriction_details[restriction]["status"] = target_status.value
                        engine.save(project)
                    else:
                        raise PermissionError("You do not have permission to approve this restriction")
                    # form locking conditional on approval status
            else:
                raise PermissionError("you do not have permission to edit this project")
        except Exception as e:
            current_app.logger.exception(str(e))
            return Response(str(e), status = 403)
        
        return "OK"
    
    return bp
