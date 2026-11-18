# Pages ---- 
from sample_tracker.datamodel import (
    Project,
    Sample,
    Person,
    Role,
)
from sample_tracker.auth import requires_auth
from sample_tracker.permissions import (
    # apply_permissions,
    get_current_person,
    can_person_edit_project,
)
from sample_tracker.utility import get_form
from odmantic import ObjectId
from flask import (
    Blueprint,
    render_template,
    session,
    current_app,
    Response,
)
def construct_bp(engine):
    bp = Blueprint("pages", __name__)

    # @bp.route("/search")
    # @requires_auth
    # def search():
    #     pass
     
    # @bp.route("/reports")
    # def reports():
    #     pass

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

    @bp.route("/users")
    @requires_auth
    def users():
        person = get_current_person(engine, session)
        try:
            if person.is_admin():
                try:
                    people = list(engine.find(Person))
                except Exception as e:
                    current_app.logger.exception(str(e))
                return render_template(
                    "pages/users.html",
                    person = person, people = people, roles = Role.values()
                )
            else:
                raise PermissionError("Admins Only")
        except Exception as e:
            current_app.logger.exception(str(e))
            Response(str(e), status=403)

        return "OK"

    @bp.route("/update_user", methods = ["POST", "GET"])
    # @bp.route("/update_user/<person_id>/<role>")
    @requires_auth
    # def update_user(person_id, role):
    def update_user():
        person = get_current_person(engine, session)
        try:
            if person.is_admin():
                form = get_form()
                print(form)
                try:
                    user = engine.find_one(
                        Person, Person.id == ObjectId(form["person_id"])
                    )
                except Exception as e:
                    current_app.logger.exception(str(e))
                try:
                    if form["update_type"] == "add":
                        user.add_roles({Role(form["role"]).value})
                    elif form["update_type"] == "remove": 
                        user.remove_roles({Role(form["role"]).value})
                    engine.save(user)
                except Exception as e:
                    current_app.logger.exception(str(e))
                return "OK"
            else:
                raise PermissionError("Admins Only")
        except Exception as e:
            current_app.logger.exception(str(e))
            Response(str(e), status=403)

    @bp.route("/savesample", methods = ['POST', 'GET'])
    @requires_auth
    def savesample():
        "Create a new sample or update an existing one"

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

        # There should always be a project id
        project_id = ObjectId(form["project_id"])

        project = engine.find_one(Project, Project.id == project_id)

        # Check that this is OK
        if not can_person_edit_project(person, project):
            return Response("Not allowed to edit this project", status = "403")

        # If there isn't a sample id then we're making a new sample
        if not form["sample_id"]:
            # projects.update_one({"project_id":project_id},{"$push":{"samples":sample}})
            sample = Sample(
                name = form["name"],
                state = form["state"],
                organism = form["organism"],
                # status
                tags = tags
            )
            # sample.tags = tags
            engine.save(sample)
            # add - unique
            project.samples.append(sample.id)
            engine.save(project)
            
            return "OK"
    
        else:
            sample = engine.find_one(Sample, Sample.id == ObjectId(form["sample_id"]))
            sample.name = form["name"]
            # sample.state = form["state"]
            # sample.organism = form["organism"]
            sample.tags = tags
            engine.save(sample)
                        
            return "OK"
        
    @bp.route("/deletesample", methods = ['POST', 'GET'])
    @requires_auth
    def deletesample():
        "Deletes a sample"

        person = get_current_person(engine, session)
        form = get_form()

        # There should always be a project id and a sample id
        project_id = ObjectId(form["project_id"])
        sample_id = ObjectId(form["sample_id"])

        project = engine.find_one(Project, Project.id == project_id)

        # Check that this person can edit this project
        if not can_person_edit_project(person, project):
            return Response("Not allowed to edit this project", status = 403)
            # raise Exception("Not allowed to edit this project")
        project.samples.pop(sample_id)
        sample = engine.find_one(Sample, Sample.id == sample_id)
        engine.save(project)
        engine.delete(sample)

        return("OK")


    return bp
