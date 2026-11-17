from sample_tracker.auth import (
    requires_auth,
)
from sample_tracker.datamodel import (
    Project,
    Person,
    ApprovalStatus,
    Role,
    Restriction,
)
from sample_tracker.utility import (
    get_form,
    deep_update,
    nest_dict,
)

from sample_tracker.permissions import (
    get_current_person,
    can_person_edit_project,
)
from bson import ObjectId
from flask import (
    Blueprint,
    Response,
    redirect,
    session,
    current_app,
    url_for,
    render_template,
)
def construct_bp(engine):
    bp = Blueprint("restrictions", __name__)

    @bp.route("/project/add_restriction", methods = ["GET", "POST"])
    @requires_auth
    def add_restriction():
        person = get_current_person(engine, session)
        form = get_form()
        project_id = form.get("project_id")
        project = engine.find_one(Project, Project.id == ObjectId(project_id))
        if can_person_edit_project(person, project):
            restrictions = {Restriction(x) for x in form.get("project_restrictions").split(",")}
            project.restrictions = list(set(project.restrictions) | restrictions)
            # don't delete exisiting restriction details when adding more
            # don't present existing restrictions in add dialog
            # allow deletion of restrictions by editors prior to initial submission
            # allow admin / relevant restriction role deletion of restrictions
            project.restriction_details = deep_update(
                project.restriction_details,
                dict(zip(
                    restrictions,
                    [{"status": ApprovalStatus.notsubmitted} for x in range(len(restrictions))]
                ))
            )
            engine.save(project)
            current_app.logger.info(form)
            # restrictions = {Restriction(x) for x in form.get("project_restrictions").split(",")}
            # current_restrictons = set(project.restrictions)
            # current_restrictons.add(restrictions)
            # project.restrictions = list(current_restrictons)
        return redirect(url_for("project.project", project_id = project_id))

    @bp.route("/project/remove_restriction/<project_id>/<restriction>") # , methods = ["GET", "POST"])
    @requires_auth
    def remove_restriction(project_id, restriction):
        # NB move to passing name not value elsewhere more URL safe
        restriction_value = Restriction[restriction].value
        person = get_current_person(engine, session)
        try:
            project = engine.find_one(Project, Project.id == ObjectId(project_id))
        except Exception as e:
            m = f"Project {project_id} not found"
            current_app.logger.exception(m + str(e))
            return Response(m, status=404)
        if person.is_admin() or project.restriction_details.get(restriction_value).get("status") == "Not Submitted" or restriction_value in person.get_roles():
            project.restrictions = list(set(project.restrictions) - {Restriction[restriction]})
            del project.restriction_details[restriction_value]
            engine.save(project)
            current_app.logger.info(f"restriction {restriction_value} removed from project {project_id}")
        else:
            return Response("No authorised to remove restriction project", status=403)
        return redirect(url_for("project.project", project_id = project_id))

    @bp.route("/project/restrictions/<project_id>/<restriction>", methods = ["GET", "POST"])
    @requires_auth
    def restrictions(project_id, restriction):
        person = get_current_person(engine, session)
        project = engine.find_one(Project, Project.id == ObjectId(project_id))
        if can_person_edit_project(person, project):
            project_restrictions = [x.value for x in project.restrictions]
            try:
                if restriction in project_restrictions:
                    restriction_details = project.restriction_details.get(restriction)
                    # allow admins and appovers to update whilst pending?
                    if restriction_details.get("status") == "Pending":
                        raise PermissionError("Cannot update project details whilst approval is pending")
                else:
                    raise Exception(f"The restriction {restriction} does not apply to the project {project_id}")
            except Exception as e:
                current_app.logger.exception(e)

            # print({restriction: {"form_data": nest_dict(get_form())}})
            project.restriction_details = deep_update(
                project.restriction_details,
                {restriction: {"form_data": nest_dict(get_form())}}
            )
            engine.save(project)
           
        else:
            return Response("No authorised to edit project", status=403)

        return render_template(
            "pages/restrictions.html",
            person = person,
            project = project,
            restriction_details = restriction_details,
            restriction = restriction,
            ApprovalStatus = ApprovalStatus,
            restriction_definition = globals().get(restriction)
        ) 

    @bp.route("/project/restriction_approval_status/", methods = ["GET", "POST"])
    @requires_auth
    def restriction_approval_status():
        person = get_current_person(engine, session)
        form = get_form()
        try:
            project = engine.find_one(Project, Project.id == ObjectId(form["project_id"]))
        except Exception as e:
            current_app.logger.exception(str(e))
        try:
            if can_person_edit_project(person, project):
                if Role(form["restriction"]) in person.get_roles_set() or person.is_admin():
                    if (ApprovalStatus(form["target-status"]) in ApprovalStatus.approver_targets() and project.restriction_details[form["restriction"]]["status"] in ApprovalStatus.approver_sources()) or person.is_admin():
                        project.restriction_details[form["restriction"]]["status"] = form["target-status"]
                        project.restriction_details[form["restriction"]]["approval_feedback"] = form["approval-feedback"]
                        engine.save(project)
                    else:
                        raise PermissionError("Transition disallowed")
                else:
                    raise PermissionError("Not an admin or approver for this restriction")
        except Exception as e:
            current_app.logger.exception(str(e))
            return Response(str(e), status=403)
            
        return "OK"
    return bp
