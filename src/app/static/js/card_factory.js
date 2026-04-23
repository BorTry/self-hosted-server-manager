const server_list = document.getElementById("server-list")

function create_server_card(name, launch_options) {
    const list_item = document.createElement("div")
    
    list_item.className = "server-item shadow round-border"
    list_item.id = name

    const image = document.createElement("img")
    image.className = "server-item-image"
    image.id = `${name}-image`
    image.src = `/static/images/${name}.jpg`
    list_item.appendChild(image)
    
    const hidden_info = document.createElement("div")
    hidden_info.className  = "server-item-hidden full-size"
    list_item.appendChild(hidden_info)
    
    const item_info = document.createElement("div")
    item_info.className = "server-item-info full-size"
    list_item.appendChild(item_info)

    create_information_page(item_info, name)
    create_hidden_page(hidden_info, name, launch_options)

    server_list.appendChild(list_item)
}

function create_information_page(parent, name) {
    const container = document.createElement("div")
    container.className = "server-info-container full-size"

    const title = document.createElement("h1")
    title.innerText = name
    title.className = "title"

    container.appendChild(title)
    container.appendChild(create_information_container(name, "player-count", "Player count", "0/20"))

    let gauge_container = document.createElement("div")
    gauge_container.className = "gauge-list"
    gauge_container.appendChild(create_gauge(`cpu-gauge-${name}`, "Cpu"))
    gauge_container.appendChild(create_gauge(`ram-gauge-${name}`, "Ram"))

    container.appendChild(gauge_container)
    parent.appendChild(container)
}

function create_information_container(name, id, title, text) {
    const container = document.createElement("div")
    container.id = `${name.replace(" ", "-")}-${id}`
    container.className = "center-content full-size"

    const text_el = document.createElement("h3")
    text_el.innerText = title

    const p = document.createElement("p")
    p.innerText = text

    container.appendChild(text_el)
    container.append(p)

    return container
}

function create_hidden_page(parent, name, launch_options) {
    let container = document.createElement("div")
    container.className = "full-size"

    let form = document.createElement("form")
    form.setAttribute("for", name)
    form.id = `${name}-form`
    form.className = "server-form full-size"

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        document.getElementById(`${name}-image`).style.borderColor = "var(--waiting)"

        let formData = new FormData(e.target);
        formData.set("name", name)
        formData.set("state", e.submitter.name)

        fetch("/backend/change_server", {
            method: "POST",
            body:formData
        });
    })

    let stop_button = document.createElement("button")
    stop_button.type = "submit"
    stop_button.innerText = "Stop Server"
    stop_button.name = "stop"
    stop_button.className = "stop_button round-border shadow"

    let start_button = document.createElement("button")
    start_button.type = "submit"
    start_button.innerText = "Start Server"
    start_button.name = "start"
    start_button.className = "round-border shadow"

    let button_container = document.createElement("div")
    button_container.appendChild(start_button)
    button_container.appendChild(stop_button)
    button_container.className = "button-container"


    container.appendChild(form)

    create_launch_option(form, name, launch_options)
    form.appendChild(button_container)
    
    parent.appendChild(container)
    
}

function create_launch_option(parent, name, launch_options) {
    if (!(name in launch_options)) return

    let frag = document.createDocumentFragment()

    let div_container = document.createElement("div")
    div_container.className = "server-form-container"

    frag.appendChild(div_container)

    for (let option of launch_options[name]) {
        div_container.appendChild(create_launch_type(name, option))
    }

    parent.appendChild(frag)
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