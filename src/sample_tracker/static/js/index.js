// const bootstrap = require("bootstrap")

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".delete-project-button").forEach(function(x) {
      x.addEventListener("click", delete_project_modal)
    })
})

function delete_project_modal() {
  let id = this.id.split("-")[1]
  document.getElementById("confirmDeleteButton").href = location.origin + "/project/delete_project/" + id
  document.getElementById("projectID").textContent = id
  new bootstrap.Modal(document.getElementById("confirmDelete")).show()
}
