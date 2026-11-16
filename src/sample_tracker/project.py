# Project ----
import re
from odmantic import (
    ObjectId,
    query,
)
from flask import (
    Flask,
    Blueprint,
    session,
    current_app,
    Response,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_from_directory,
)
from pathlib import Path
from werkzeug.utils import secure_filename
from sample_tracker.utility import (
    get_form,
    args_to_dict,
    nest_dict,
    deep_update,
)
from sample_tracker.auth import requires_auth
from sample_tracker.permissions import (
    get_current_person,
    can_person_see_project,
    can_person_create_project,
    can_person_edit_project,
    can_change_project_ownership,
)
from sample_tracker.datamodel import (
    Project,
    Person,
    File,
    Restriction,
    ApprovalStatus,
    Authorizations,
)
from sample_tracker.restrictions import *

def construct_bp(engine):
    bp = Blueprint("project", __name__)# , url_prefix="/project")

    @bp.route("/project/<project_id>")
    @requires_auth
    def project(project_id):
        try:
            person = get_current_person(engine, session)
        except Exception as e:
            current_app.logger.exception(e)

        # Get the project
        try:
            project = engine.find_one(
                Project, Project.id == ObjectId(project_id)
            )
        except Exception as e:
            current_app.logger.exception("No project found" + str(e))
        
        # Check they are allowed to see this
        try:
            if not can_person_see_project(person, project):
                m = (
                    f"{person.username} tried to view "
                    f"{str(project.id)} which they are not authorized to view"
                )
                current_app.logger.exception(m)
                raise PermissionError(m)
        except Exception as e:
            return Response(
                str(e),
                # "Not allowed to view this project",
                status="403", mimetype="text/plain"
            )

        # We want to swap the owner on the project for the owner name ??
        owner = engine.find_one(Person, Person.id == project.owner)
        # project.owner = owner.id
        project_owner = owner.username
        # engine.save(project)
        # p
        attachments = []
        if project.attachments != []:
            try:
                attachments = list(engine.find(
                    File, query.in_(File.id, project.attachments))
                )
            except Exception as e:
                current_app.logger.exception(e)

        # can remove restrictions if:
        # - admin
        # - editor and not yet submitted
        # - is approver for the restriction
        
        # Show only restrictions not already applied to the project in the
        # add restrictions dialog
        current_restrictions = project.restrictions_values_set()
        all_restrictions = Restriction.values()
        restrictions = list(current_restrictions ^ all_restrictions)

        # Is approver for any restrictions
        # shows remove restrictions buttons, additional logic
        # checks what they can approve and only shows remove buttons for
        # relevant restrictions
        # is_approver = any(x in person.get_roles() for x in all_restrictions)
        any_unsubmitted = any(
            x == "Not Submitted" for x in [
                v.get('status') for k,v in project.restriction_details.items()
            ]
        )

        users = {
            str(u.id): u.username for u in list(engine.find(
                Person, Person.id.in_(
                    [ObjectId(x) for x in project.authorizations.keys()]
                )
            ))
        }

        return render_template(
            "pages/project.html",
            person = person, project = project,
            can_edit = can_person_edit_project(person, project),
            can_view = can_person_see_project(person, project),
            can_create = can_person_create_project(person),
            attachments = attachments,
            project_owner = project_owner,
            restrictions = restrictions,
            any_unsubmitted = any_unsubmitted,
            users = users,
            restriction = Restriction,
            approval_status = ApprovalStatus,
        )

    @bp.route("/editproject",defaults={"project_id":None})
    @bp.route("/editproject/<project_id>")
    @requires_auth
    def editproject(project_id):
        try:
            person = get_current_person(engine, session)
        except Exception as e:
            current_app.logger.exception("Could not find user" + str(e))
            # return redirect(url_for("login"))
        
        # They could be starting a new project or editing an existing
        # one.
        project = None
        new = False
        # If it's a new project they need to be an admin
        # if project_id is None and not person.is_admin:
        #     raise Exception("Admins only")

        if project_id is None and person.can_create_project():
            project = Project(
                owner = person.id,
                title = "",
                authorizations = dict(
                    {str(person.id): dict({"edit":0, "view":0})}
                )
            )
            new = True
            # engine.save(project)
        else:
            project = engine.find_one(Project, Project.id == ObjectId(project_id))
            if not project:
                raise Exception(f"Project {project_id} not found")

            # To do this they either need to be an admin or they need to own the project
            if not can_person_edit_project(person, project):
                current_app.logger.info(f"{person.username} attempted to edit {project.id}")
                return Response("You don't have permission to edit this project", status="403")

        users = {str(u.id): u.username for u in list(engine.find(Person))}

        return render_template(
            "pages/edit_project.html",
            new = new, project = project, person = person, users = users,
            authorizations = Authorizations
        )

    @bp.route("/project/update_user_auth", methods = ['POST', 'GET'])
    @requires_auth
    def update_user_auth():
        person = get_current_person(engine, session)
        form = get_form()
        print(form)
        project = engine.find_one(Project, Project.id == ObjectId(form["project_id"]))
        # print(project)
        if can_person_edit_project(person, project):
            uid = str(engine.find_one(Person, Person.username == form["user-add"]).id)
            if form.get("remove") == 'true':
                del project.authorizations[uid]
                engine.save(project)
                return "OK"
            new_auth = {uid: {}}
            if form.get("set-view", False):
                new_auth[uid].update({'view':0})
            if form.get("set-edit", False):
                new_auth[uid].update({'edit':0})
            project.authorizations.update(new_auth)
            engine.save(project)
            return "OK"
        else:
            return Response("not authorised to update project", status=403)

    @bp.route("/saveproject", methods = ['POST', 'GET'])
    @requires_auth
    def saveproject():
        "Create a new project or update an existing one"

        person = get_current_person(engine, session)
        form = get_form()

        tags = {}
        try:
            tags_list = form["tags"].split(",")
            if(tags_list == ""):
                tags = {}
            else:
                tags = dict(zip(tags_list, tags_list))
        except Exception as e:
            current_app.logger.exception(e)

        # If there isn't a project id then we're making a new project
        if not form.get("project_id") and can_person_create_project(person):
            # We need an owner
            owner = engine.find_one(Person, Person.username == form["owner"])# .id

            project = Project(
                title = form["title"],
                description = form["description"],
                owner = owner.id,
                # status = "proposed",
                # date_created,
                tags = tags,
                # samples = [],
                authorizations = {
                    str(owner.id): {"edit":0, "view":0},
                    # The person who created the project should also be able
                    # to see / edit it even if they are not the owner
                    str(person.id): {"edit":0, "view":0}
                }
            )
                
            engine.save(project)
            return str(project.id)

        else:

            # We're editing an existing project
            project = engine.find_one(Project, Project.id == ObjectId(form["project_id"]))

            # Check this person is allowed to do this
            if can_person_edit_project(person, project):
                project.title = form["title"]
                project.description = form["description"]
                project.tags = tags
                engine.save(project)

            # They may want to change the owner
            if form["owner"] and can_change_project_ownership(person, project):
                owner = engine.find_one(Person, Person.username == form["owner"])
                if project.owner != owner.id:
                    project.owner = owner.id
                    # ensure the owner also has permissions set explicitly
                    project.authorizations = deep_update(
                        project.authorizations,
                        {str(owner.id): {"edit":0, "view":0}}
                    )
                    engine.save(project)

            return str(project.id)

    @bp.route("/checkowner", methods = ['POST', 'GET'])
    @requires_auth
    def checkowner():
        "Used to check usernames for new projects when they press the check button"
        person = get_current_person(engine, session)
        form = get_form()
        # project = engine.find_one(Project, Project.id == ObjectId(form["project_id"]))
        # if can_change_project_ownership(person, project):
        if can_person_create_project(person):
            found_person = engine.find_one(Person, Person.username == form["username"])
            person_text = f"{found_person.username} ({form['username']})"
            return person_text
        else:
            return Response("Access Denied", status = 403, mimetype="text/plain")

    @bp.route("/project/upload_project_attachment/<project_id>", methods = ["GET", "POST"])
    @requires_auth
    def upload_project_attachment(project_id):
        project_id = ObjectId(project_id)
        person = get_current_person(engine, session)
        project = engine.find_one(Project, Project.id == project_id)
        if can_person_edit_project(person, project):
            project_id = str(project_id)
            if request.method == "POST":
                form = request.form.to_dict()
                if len(request.files) > 1:
                    raise Exception("Multiple files supplied when one expected!")
                id = list(request.files.keys())[0]
                # print(id)
                if id not in request.files:
                    flash("No file part")
                    # {"error:" "importError"}
                    return redirect(request.url)
                file = request.files[id]
                print(file.filename)
                if file.filename == "":
                    flash("No selected file")
                    # {"error:" "noFileFound"}
                    return(request.url)
                if file:
                    # consider setting the object ID first so
                    # the filepath can include the ID of the file object
                    # this would make it easier to rebuild the DB from
                    # the file system should the need arise
                    filename = secure_filename(file.filename)
                    project_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "projects" / project_id

                    # form = args_to_dict(request.form)
                    form = request.form.to_dict()
                    restriction = form.get("restriction", None)
                    if restriction:
                        project_dir = project_dir / restriction

                    project_dir.mkdir(parents=True, exist_ok=True)
                    file_path = project_dir / filename
                    file.save(file_path)
                    file_object = File(path = str(file_path))
                    engine.save(file_object)
                    project = engine.find_one(Project, Project.id == ObjectId(project_id))
                    project.attachments.append(file_object.id)

                    if restriction:
                        project.restriction_details = deep_update(
                            project.restriction_details,
                            {
                                restriction: {
                                    "form_data": {
                                        id.split("_")[0]: {
                                            id.split("_")[1]: {
                                                "objectId": str(file_object.id),
                                                "filename": filename
                                            }
                                        }
                                    }
                                }
                            }
                        )
                    engine.save(project)
                    
                    if restriction:
                        resp = {
                            "file_id": str(file_object.id),
                            "filename": filename
                        }
                        return resp
        else:
            return Response(
                "Not allowed to edit this project",
                status="403", mimetype="text/plain"
            )
        return redirect(url_for("project.project", project_id = project_id))

    @bp.route("/project/delete_project/<project_id>")
    @requires_auth
    def project_delete(project_id):
    # Implement "are you sure? dialog"
        project_id = ObjectId(project_id)
        person = get_current_person(engine, session)
        project = engine.find_one(Project, Project.id == project_id)
        if can_person_edit_project(person, project):
            engine.delete(project)
        else:
            return Response(
                "Not allowed to edit this project",
                status="403", mimetype="text/plain"
            )
        return redirect(url_for("index.index", project_id = project_id))

    @bp.route("/project/delete_attachment/<project_id>/<attachment_id>")
    @requires_auth
    def project_delete_attachment(project_id, attachment_id):
    # Implement "are you sure? dialog"
        project_id = ObjectId(project_id)
        attachment_id = ObjectId(attachment_id)
        person = get_current_person(engine, session)
        project = engine.find_one(Project, Project.id == project_id)
        if can_person_edit_project(person, project):
            if attachment_id in project.attachments:
                attachment = engine.find_one(File, File.id == attachment_id)
                Path(attachment.path).unlink()
                engine.delete(attachment)
                project.attachments.pop(project.attachments.index(attachment_id))
                engine.save(project)
            else:
                Exception("This file is not attached to this project")
        else:
            return Response(
                "Not allowed to edit this project",
                status="403", mimetype="text/plain"
            )
        return redirect(url_for("project.project", project_id = project_id))

    @bp.route("/project/download_attachment/<project_id>/<attachment_id>")
    @requires_auth
    def project_download_attachment(project_id, attachment_id):
        project_id = ObjectId(project_id)
        attachment_id = ObjectId(attachment_id)
        person = get_current_person(engine, session)
        project = engine.find_one(Project, Project.id == project_id)
        if can_person_see_project(person, project):
            if attachment_id in project.attachments:
                attachment = engine.find_one(File, File.id == attachment_id)
                dir = Path(attachment.path).parent.resolve()
                filename = attachment.get_filename()
                # print(dir)
                # print(filename)
                rel_filepath = "/".join(Path(attachment.path).parts[-3:])
                current_app.logger.info(
                    f"{person.username} downloaded {rel_filepath}"
                )
                return send_from_directory(dir, filename, as_attachment=True)
            else:
                Exception("This file is not attached to this project")
        else:
            return Response(
                "Not allowed to view this project",
                status="403", mimetype="text/plain"
            )
        return redirect(url_for("project.project", project_id = project_id))

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
                else:
                    raise Exception(f"The restriction {restriction} does not apply to the project {project_id}")
            except Exception as e:
                current_app.logger.exception(e)

            # print({restriction: {"form_data": nest_dict(get_form())}})
            project.restriction_details = deep_update(
                project.restriction_details, # [restriction]["form_data"],
                {restriction: {"form_data": nest_dict(get_form())}}
            )
            # project.restriction_details[restriction]["form_data"].update(nest_dict(get_form()))
            engine.save(project)
           
        else:
            return Response("No authorised to edit project", status=403)

        return render_template(
            "pages/restrictions.html",
            project = project,
            restriction_details = restriction_details,
            restriction = restriction,
            ApprovalStatus = ApprovalStatus,
            restriction_definition = globals().get(restriction)
        ) 
    
    return bp
