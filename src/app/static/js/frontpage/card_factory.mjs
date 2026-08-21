export default function build_request_form(name) {
    const hidden_info = document.createElement("div")
    hidden_info.className = "server-item-hidden full-size"
    
    let form = document.getElementById(name+"-form")

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        document.getElementById(name).style.borderColor = "var(--waiting)"
        
        let formData = new FormData(e.target);

        fetch("api/container/"+name+"/"+e.submitter.name, {
            method: "POST",
            body:formData
        });
    })
}