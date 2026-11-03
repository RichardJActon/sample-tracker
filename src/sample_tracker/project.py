def construct_bp(engine):
    bp = Blueprint("project", __name__)# , url_prefix="/project")
    @bp.route("/project/upload_project_attachment/<project_id>", methods = ["GET", "POST"])
    @requires_auth # needs admin/role check
    def upload_project_attachment(project_id):
        project_id = str(project_id)
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                # {"error:" "importError"}
                return redirect(request.url)
            file = request.files["file"]
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
                project_dir.mkdir(parents=True, exist_ok=True)
                file_path = project_dir / filename
                file.save(file_path)
                file_object = File(path = str(file_path))
                engine.save(file_object)
                project = engine.find_one(Project, Project.id == ObjectId(project_id))
                project.attachments.append(file_object.id)
                engine.save(project)
                # return json
                # {"data:" {"filePath": file_path}}
                
                # project.update_one({
                #     "project_id": project_id,
                #     "attachments.attachement_id": 
                # })
        return redirect(url_for("project.project", project_id = project_id))

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
                print(dir)
                print(filename)
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

    return bp
