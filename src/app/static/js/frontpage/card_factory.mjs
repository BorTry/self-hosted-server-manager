const server_list = document.getElementById("server-list")

export default function build_request_form(name, launch_options) {
    const hidden_info = document.createElement("div")
    hidden_info.className = "server-item-hidden full-size"

    create_hidden_page(name, launch_options)
}

function create_hidden_page(name, launch_options) {
    let form = document.getElementById(name+"-form")

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        document.getElementById(name).style.borderColor = "var(--waiting)"
        let change = e.submitter.name
        
        let formData = new FormData(e.target);

        fetch("api/container/"+name+"/"+e.submitter.name, {
            method: "POST",
            body:formData
        });
    })

    if (!(name in launch_options)) return

    let div_container = document.getElementById(name+"-form-container")

    for (let option of launch_options[name]) {
        div_container.appendChild(create_launch_type(name, option))
    }
}

function create_launch_type(name, option) {
    let option_container = document.createElement("div")
    let label = document.createElement("label")
    label.setAttribute("for", `${name}-${option.name}`)
    label.innerText = option.name
    
    let container;
    switch (option.type) {
        case "select":
            container = document.createElement("select")
            container.name = option.name
            container.id = `${name}-${option.name}`
            container.className = "round-border shadow"

            for (let val of option.values) {
                let child = document.createElement("option")
                child.value = val
                child.innerText = val

                container.appendChild(child)
            }
            break;
            
        default:
            break;
    }

    option_container.appendChild(label)
    option_container.appendChild(container)
    return option_container
}