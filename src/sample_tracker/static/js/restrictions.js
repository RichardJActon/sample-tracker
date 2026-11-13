
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("[id$=_upload]").forEach(function(x) {
        x.addEventListener("click", upload_attachment)
    })
    document.querySelectorAll("input[type=file]").forEach(function(x) {
      // NB disable upload unless a new file is specified as clicking upload uploads the dummy file with this setup
        if(x.dataset.filename) {
            dummyFile = new File(
                ["dummy content"],
                x.dataset.filename,
                {
                    type: "text/plain",
                    lastModified: new Date() 
                }
            )
            dt = new DataTransfer()
            dt.items.add(dummyFile)
            x.files = dt.files
        }
    })
})

const path = location.pathname.split("/")
let project_id = path.at(-2)

function upload_attachment() {
    let form = this.parentElement.parentElement.parentElement
    form.preventDefault
    let formData = new FormData(form) 
    formData.append("restriction", path.at(-1) )
    // console.log(formData.forEach(function(x){console.log(x)}))
    fetch("/project/upload_project_attachment/" + project_id, {
        method: "POST",
        body: formData
    })
    .then(response => {
        if(!response.ok) throw new Error("Request failed");
        return response.text();
    })
    .then(response => {
        let del_file = form.querySelector("[id$=_delete]")
        del_file.setAttribute("class", "button btn btn-danger")
        let dl_file = form.querySelector("[id$=_download]")
        dl_file.setAttribute("class", "button btn btn-primary")
        let upload_file = form.querySelector("[id$=_upload]")
        upload_file.disabled = dl_file.disabled

        const resp_json = JSON.parse(response)
        del_file.setAttribute(
          "href",
          "/project/delete_attachment/" + project_id + "/" + resp_json.file_id
        )
        dl_file.setAttribute(
          "href",
          "/project/download_attachment/" + project_id + "/" + resp_json.file_id
        )
        // del_file.dataset.filename = resp_json.filename
        // dl_file.dataset.filename = resp_json.filename 
        // window.location.reload()
    })
    .catch(message => {
        console.log(message)
        console.log("error uploading attachment")
        return
    })
}
