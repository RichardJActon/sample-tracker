// const bootstrap = require("bootstrap")

document.addEventListener("DOMContentLoaded", function() {

    // document.getElementById("add_sample").addEventListener("click", show_new_sample)
    // document.querySelectorAll(".editsample").forEach(function(es) {
    //     es.addEventListener("click", show_new_sample)
    // })
    // document.getElementById("save_sample").addEventListener("click", save_sample)
    // document.querySelectorAll(".deletesample").forEach(function(es) {
    //     es.addEventListener("click", delete_sample)
    // })

    document.getElementById("add_restriction").addEventListener("click", show_restrictions_modal)
    document.getElementById("add_restrictions").addEventListener("click", add_restriction)

    document.querySelectorAll(".delete-attachment-button").forEach(function(x) {
      x.addEventListener("click", delete_attachment_modal)
    })

    document.querySelectorAll(".remove-restriction-button").forEach(function(x) {
      x.addEventListener("click", remove_restriction_modal)
    })

    document.querySelectorAll(".submit-approval-request").forEach(function(x) {
        x.addEventListener("click", confirm_restriction_submission)
    })
})

function delete_attachment_modal() {
    document.getElementById("confirmDeleteButton").href = this.dataset.href
    const cid = this.id.split("-")
    document.getElementById("object-name").textContent = this.parentElement.parentElement.querySelector(".filename").textContent
    document.getElementById("object-id").textContent = cid[1]
    document.getElementById("confirmDeleteMessage").textContent = "Do you want to permenantly delete the attachment?"
    new bootstrap.Modal(document.getElementById("confirmDelete")).show()
}

function remove_restriction_modal() {
    document.getElementById("confirmDeleteButton").href = this.dataset.href
    const cid = this.id.split("-")
    document.getElementById("object-name").textContent = this.parentElement.parentElement.querySelector(".restriction").textContent
    document.getElementById("object-id").textContent = cid[1]
    document.getElementById("confirmDeleteMessage").textContent = "Do you want to remove this restriction?"
    new bootstrap.Modal(document.getElementById("confirmDelete")).show()
}

// function delete_sample() {
//     // We need to get the project id and sample id from 
//     // the start of the table row in which the delete 
//     // button was found.

//     let ids = this.parentElement.parentElement.find("td").first.textContent
//     let project_sample = ids.split("-")

//     this.disabled = true

//     let row_to_delete = this.parentElement.parentElement
//     fetch("/deletesample", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/x-www-form-urlencoded"
//         },
//         body: new URLSearchParams({
//             project_id: project_sample[0],
//             sample_id: project_sample[1] 
//         })
//     })
//     .then(response => {
//         if(!response.ok) throw new Error("Request failed");
//         return response.text();
//     })
//     .then(() => {
//         row_to_delete.remove()
//     })
//     .catch(() => {
//         this.disabled = false
//         console.log("Failed to delete sample")
//         return
//     })
// }

// function save_sample() {
//     // We need the project id
//     let project_id = location.pathname.split("/").pop()
//     if (project_id == "project") {
//         project_id = ""
//     }

//     // We need to determine if this is a new sample or editing an existing one
//     let sample_id = document.getElementById("sample_modal_header").dataset.sample_id

//     let something_failed = false

//     // We need to collect the standard features
//     let name = document.getElementById("sample_name").value.trim()
//     if (name) {
//          document.getElementById("sample_name").style.borderColor = "rgb(222, 226, 230"
//     }
//     else {
//         document.getElementById("sample_name").style.borderColor = "red"
//         something_failed = true
//     }
   
//     // We then need the values for the tags
//     let tag_values = []
//     document.querySelectorAll(".tag_value_input").forEach(function(t) {
//         let value = t.value.trim()
//         if (value) {
//             t.style.borderColor = "rgb(222, 226, 230"
//             tag_values.push(value)
//         }
//         else {
//             t.style.borderColor = "red"
//             something_failed = true
//         }
//     })

//     if (something_failed) {
//         return
//     }

//     // Now we can add/edit this
//     document.getElementById("save_sample").disabled = true
//     fetch("/savesample", {
//         method: "POST",
//         headers: { "Content-Type": "application/x-www-form-urlencoded"},
//         body: new URLSearchParams({
//             project_id: project_id,
//             sample_id: sample_id,
//             name: name,
//             // state: state,
//             // organism: organism,
//             tags: tag_values
//         })
//     })
//     .then(response => {
//         if(!response.ok) throw new Error("Request failed");
//         return response.text();
//     })
//     .then(project_id => {
//         window.location.reload()
//     })
//     .catch(message => {
//         document.getElementById("errormessage").textContent = "Failed to save project"
//         document.getElementById("editprojecterror").show()
//         document.getElementById("save_sample").disabled = false
//         return
//     })

// }

// function show_new_sample() {
//     // We might have come from the "new sample" button, or we might
//     // be editing an existing sample
//     const input_fields = document.getElementById("editsamplediv").querySelectorAll("input");

//     if (this.classList.contains("editsample")) {
//         // We're editing an existing sample
//         const row_data = this.parentElement.parentElement.querySelectorAll("td");

//         const header = document.getElementById("sample_modal_header");
//         header.textContent = "Edit Sample " + row_data[0].textContent;

//         const project_sample = row_data[0].textContent.split("-");
//         header.dataset.sampleId = project_sample[1];

//         for (let i = 0; i < input_fields.length; i++) {
//             input_fields[i].value = row_data[i + 1].textContent.trim();
//         }
//     } else {
//         // We're starting a new sample
//         input_fields.forEach(f => f.value = "");
//         const header = document.getElementById("sample_modal_header");
//         header.dataset.sampleId = "";
//         header.textContent = "Add Sample";
//     }

//     // Blank the contents
//     new bootstrap.Modal(document.getElementById("editsamplediv")).show();
// }   

function show_restrictions_modal() {
    new bootstrap.Modal(document.getElementById("selectRestrictions")).show()
}

function add_restriction() {
    let project_id = location.pathname.split("/").pop()
    project_restrictions = Array.from(
        document.getElementById("restrictions-list").selectedOptions
    ).map(opt => opt.value)

    fetch("/project/add_restriction", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({
            project_id: project_id,
            project_restrictions: project_restrictions,
        })
    })
    .then(response => {
        if(!response.ok) throw new Error("Request failed");
        return response.text();
    })
    .then(project_id => {
        window.location.reload()
    })
    .catch(message => {
        document.getElementById("add-restrictions-error").textContent = "Failed to add restrictions"
        return
    })
}

function confirm_restriction_submission() {
    const restriction = this.dataset.restriction
    const submit_btn = document.createElement('button')
    submit_btn.textContent = "Submit"
    submit_btn.classList.add('btn')
    // submit_btn.classList.add('btn-sm')
    submit_btn.classList.add('btn-danger')
    submit_btn.id = "submit-restriction-button"
    submit_btn.dataset.restriction = restriction
    submit_btn.addEventListener("click", submit_restriction)
    document.getElementById("confirmDeleteButton").replaceWith(submit_btn)
    document.getElementById("confirmDeleteMessage").textContent = `
        Are you sure you want to submit this restriction for approval?
        You will be unable to update the details of the request after this point unless the person approving your project for this restriction requests changes to the submission prior to approval.
        ` 
    new bootstrap.Modal(document.getElementById("confirmDelete")).show()
}

function submit_restriction() {
    const project_id = location.pathname.split("/").pop()
    const restriction = document.getElementById("submit-restriction-button").dataset.restriction
    
    fetch("/approval_requests", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({
            project_id: project_id,
            status: "Pending",
            restriction: restriction,
        })
    })
    .then(response => {
        if(!response.ok) throw new Error("Request failed");
        return response.text();
    })
    .then(project_id => {
        bootstrap.Modal.getInstance(document.getElementById("confirmDelete")).hide()
        document.getElementById("submit-approval-request-" + restriction).disabled = true
        location.reload()
    })
    .catch(message => {
        console.log("Failed to submit restriction for approval")
        return
    })
}
