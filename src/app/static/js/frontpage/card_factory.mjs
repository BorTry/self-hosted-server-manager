export default function build_request_form(name) {
    const hidden_info = document.createElement("div")
    hidden_info.className = "server-item-hidden full-size"
    
    let form = document.getElementById(name+"-form")

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        document.getElementById(name).style.borderColor = "var(--waiting)"
        
        const tmp_form_data = new FormData(e.target)
        const form_data = new FormData()
        const all_opts = []

        for (const [key, value] of tmp_form_data.entries()) {
            all_opts.push({"lom_name": key, "lo_name": value})
        }

        form_data.append("launch_opts", JSON.stringify(all_opts))

        fetch("api/container/"+name+"/"+e.submitter.name, {
            method: "POST",
            body:form_data
        });
    })
}