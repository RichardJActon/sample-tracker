document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("checkowner").addEventListener("click", checkowner);
    document.getElementById("saveproject").addEventListener("click", saveproject);

    document.getElementById("addtag").addEventListener("click", add_tag);
    document.querySelectorAll(".tagclose").forEach(function(el) {
        el.addEventListener("click", remove_tag)
    });
    
    document.getElementById("user-add").addEventListener("change", current_permissions);
    document.getElementById("add-user").addEventListener("click", update_user_auth);
    
})

function update_user_auth(x, remove = false) {
    // NB require other form updates to be saved before updating user auth
    const form = document.getElementById("project-auth")
    let formData = new FormData(form)
    const project_id = location.pathname.split("/").pop()
    formData.append("project_id", project_id)
    // console.log(remove)
    formData.append("remove", remove)
    form.preventDefault
    fetch("/project/update_user_auth",{
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error("Request failed");
        return response.text()
    })
    .then(() => {
        location.reload()
    })
    .catch((message) => {
        console.log(message)
    })
}

function remove_user() {
    update_user_auth(x = null, remove = true)
}

function current_permissions() {
    // set the checkboxes and buttons based on the value for any existing user
    // that is selected, set the buttons to update & remove instead of add for
    // existing users
    const user = document.getElementById("username-" + this.value)
    if (user != null) {
        const add_user_btn = document.getElementById("add-user")
        add_user_btn.textContent = " Update User "
        let remove_btn = document.createElement("button")
        remove_btn.className = "btn btn-danger btn-sm"
        remove_btn.id = "remove-user"
        remove_btn.textContent = " Remove User "
        add_user_btn.after(remove_btn)
        document.getElementById("remove-user").addEventListener("click", remove_user)
        
        let edit = document.getElementById("set-edit")
        edit.checked = false
        let view = document.getElementById("set-view")
        view.checked = false
        user.parentElement.parentElement.querySelectorAll(".auth").forEach(x => {
            if (x.textContent == "edit") {
                edit.checked = true
                return
            }
            if (x.textContent == "view") {
                view.checked = true
                return
            }
        })
    } else {
        document.getElementById("add-user").textContent = " Add User "
        document.getElementById("remove-user")?.remove()
    }
}

// let image_upload_endpoint = "/upload_project_attachment/" + location.pathname.split("/").pop()
const easyMDE = new EasyMDE({
    // autosave: {enabled = true, delay = 1000, submit_delay: 5000},
    // uploadImage: true,
    indentWithTabs: false,
    // imageUploadEndpoint = image_upload_endpoint,
    element: document.getElementById("project_description")
})

function remove_tag() {
    this.parentElement.remove();
}

function add_tag() {
    let tag_name = document.getElementById("new_tag").value;
    const tagre = /^[\w\-]{1,128}$/;

    const tagModal = new bootstrap.Modal(document.getElementById("invalidTagError"))
    if(!tagre.test(tag_name)) {
        const tagerror = 'Invalid tag (only alphanumeric values -/_ less than 128 characters)'
        document.getElementById("tagErrorMessage").textContent = tagerror
        tagModal.show()
        throw new Error(tagerror)
    }

    if (!tag_name) {
        return
    }

    // Check for uniqueness
    let found_tag = false
    document.querySelectorAll(".tag_value").forEach(function(tag) {
        if(tag_name == tag.textContent) {
            found_tag = true
        }
    })

    if (found_tag) {
        return
    }

    // Add the tag
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-sm btn-secondary";

    const tagSpan = document.createElement("span");
    tagSpan.className = "tag_value";
    // attribute example tagSpan.setAttribute("tag_value", tag_name);
    tagSpan.textContent = tag_name;

    const closeSpan = document.createElement("span");
    closeSpan.className = "tagclose";
    // closeSpan.textContent = "&nbsp;&times;";
    closeSpan.textContent = "\u00A0\u00d7";

    btn.appendChild(tagSpan);
    btn.appendChild(closeSpan);

    document.getElementById("added_tags").appendChild(btn);
    // possible XSS for user generated tag name
    // document.getElementById("added_tags").insertAdjacentHTML(
    //     `<button type="button" class="btn btn-sm btn-secondary">
    //         <span="tag_value">${tag_name}</span>
    //         <span class="tagclose"> &times;</span>
    //     </button>
    //     `
    // )
        
    document.querySelectorAll(".tagclose").forEach(function(el) {
        el.removeEventListener("click", remove_tag)
        el.addEventListener("click", remove_tag)
    })
    
    document.getElementById("new_tag").value = "";
}

function saveproject() {
    // Check we've got enough information to save the project

    // Do we have a project ID. It's the end of the URL if it's
    // there.  If it's just editproject then there's no id and
    // we're making a new project
    let project_id = location.pathname.split("/").pop()
    if (project_id == "editproject") {
        project_id = ""
    }

    //  Is there an owner
    const editModal = new bootstrap.Modal(document.getElementById("editprojecterror"))
    let project_owner = ""
    if (document.getElementById("checkedname").textContent) {
        project_owner = document.getElementById("checkedname").dataset.username
    } else {
        // This is an error if this is a new project
        if (!project_id) {
            document.getElementById("errormessage").textContent = "You need to set the project owner"
            editModal.show()
            return
        }
    }

    let project_title = document.getElementById("project_title").value

    // Error if not
    if (! project_title) {
            document.getElementById("errormessage").textContent = "You need to supply a project title"
            editModal.show()
        return
    }

    // let project_description = $("#project_description").val()
    let project_description = easyMDE.value()

    // Error if not
    if (! project_description) {
        document.getElementById("errormessage").textContent = "You need to supply a project description"
        editModal.show()
        return
    }

    // Do we have any tags?
    let tag_list = []
    document.querySelectorAll(".tag_value").forEach(function(tag) {
        tag_list.push(tag.textContent)
    })

    // We can go ahead and edit the project.
    document.getElementById("saveproject").disabled = true
    fetch("/saveproject", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            project_id: project_id,
            owner: project_owner,
            title: project_title,
            description: project_description,
            tags: tag_list
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("Request failed");
        return response.text()
    })
    .then(project_id => {
        window.location.href = "/project/" + project_id
    })
    .catch(() => {
        document.getElementById("errormessage").textContent = "Failed to save project"
        editModal.show()
        document.getElementById("saveproject").disabled = false;
    })
}

function checkowner() {
    let username = document.getElementById("project_owner").value
    let project_id = document.getElementById("project_id").textContent
    let base_url = location.origin

    if (!username) {
        return
    }

    document.getElementById("checkowner").textContent = "Checking"
    document.getElementById("checkedname").textContent = ""
    document.getElementById("checkedname").dataset.username = username

    fetch(base_url + "/checkowner", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            username: username,
            project_id: project_id
        })
    })
    .then(response => {
        // request failures not handeled by default in vanilla
        if(!response.ok) throw new Error("Request failed");
        return response.text();
    })
    .then(userstring => {
        document.getElementById("checkedname").textContent = userstring;
        const btn = document.getElementById("checkowner");
        btn.textContent = "Found!";
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-success");
        
    })
    .catch(() => {
        document.getElementById("checkedname").dataset.username = "";
        const btn = document.getElementById("checkowner");
        btn.textContent = "Not Found!";
        btn.classList.remove("btn-primary");
        btn.classList.remove("btn-success");
        btn.classList.add("btn-danger");
        // ?
        setTimeout(() => {
            btn.textContent = "Check user";
            btn.classList.remove("btn-danger");
            btn.classList.add("btn-primary");
        }, 2000);
    })
}
