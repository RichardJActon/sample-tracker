// const bootstrap = require("bootstrap")

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".delete-project-button").forEach(function(x) {
      x.addEventListener("click", delete_project_modal)
    })
})

function delete_project_modal() {
  let id = this.id.split("-")[1]
  document.getElementById("confirmDeleteButton").href = location.origin + "/project/delete_project/" + id
  document.getElementById("object-name").textContent =  this.parentElement.parentElement.querySelector(".title").textContent
  document.getElementById("object-id").textContent = id
  document.getElementById("confirmDeleteMessage").textContent = "Do you want to permanantly delete this Project?"
  new bootstrap.Modal(document.getElementById("confirmDelete")).show()
}
