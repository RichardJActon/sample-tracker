document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".update-user-button").forEach(function(x) {
        x.addEventListener("click", update_user)
    })
})

function update_user() {
    const formData = new FormData(this.parentElement)
    const id = this.id.split("-")
    formData.append("update_type", id[0])
    formData.append("person_id", id[1])
    fetch("/update_user", {
        method: "POST",
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error("Request failed");
        return response.text()
    })
    .then(() => {location.reload()})
    .catch(message => {console.log(message)})
}
