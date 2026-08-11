const ADD_SERVER_FORM = document.getElementById("add_server_form")
const SERVER_STREAM = new EventSource("/api/admin/add_container")

const PORT_ADD_BUTTON = document.getElementById("port-add-button")
const PORT_LIST = document.getElementById("port-list")

const parent_element = document.getElementById("dropdown-menus")
const form_container = document.getElementById("add_server_dropdown")

const job_queue = document.getElementById("job-queue-list")

SERVER_STREAM.addEventListener("update", (event) => {
    const data = JSON.parse(event.data)

    const status_element = document.getElementById("status_" + data.server_id)

    if (!status_element) {
        const job_container = create_job_element(data)

        job_queue.appendChild(job_container)
    } else {
        const element_container = document.getElementById("server_" + data.server_id)

        status_element.innerText = data.success ? "Success" : "Failed"
        status_element.style.color = data.success ? "var(--online)" : "var(--offline)"

        element_container.dataset.done = true

        if (data.success) return

        const error_box = document.getElementById("error_" + data.server_id)
        const parent = error_box.parentElement

        error_box.innerText = data.msg
        parent.style.display = "block"
    }
})

SERVER_STREAM.addEventListener("close", (event) => {
    SERVER_STREAM.close()
})

ADD_SERVER_FORM.addEventListener("submit", (e) => {
    e.preventDefault();
        
    const form_data = new FormData(e.target);

    const h_ports = form_data.getAll("host_port") 
    const s_ports = form_data.getAll("server_port") 
    const port_types = form_data.getAll("port_type")

    const len = h_ports.length

    const port_mapping = []   

    for (let index = 0; index < len; index++) {
        port_mapping.push({
            host_port: h_ports[index],
            server_port: s_ports[index],
            port_type: port_types[index]
        })
    } 

    form_data.set("port_mapping", port_mapping)

    form_data.delete("host_port")
    form_data.delete("server_port")
    form_data.delete("port_type")

    for (let [key, value] of form_data.entries()) {
        if (key === "image") continue
        console.log(`${key}: ${value}`);
    }

    /*fetch("/api/admin/add_container", {
        method: "POST",
        body: formData
    })*/
})

PORT_ADD_BUTTON.addEventListener("click", (event) => {
    PORT_LIST.appendChild(create_port_item())
    // change the size of the "drop down window" to fit
    form_container.style.height = "auto"
    form_container.style.height = parent_element.style.height = `${form_container.scrollHeight}px`
})

function create_job_element(data) {
    const div_container = document.createElement("div")
    div_container.className = "job-queue-item round-border shadow"
    div_container.id = "server_" + data.server_id
    
    div_container.appendChild(create_inline_text("Name: ", data.name))
    div_container.appendChild(create_inline_text("Status: ", "Working...", "status_" + data.server_id))
    div_container.appendChild(create_inline_text("Started: ", "0s", "start_" + data.server_id))
    div_container.appendChild(create_error_box(data.server_id))

    div_container.dataset.timestamp = Date.now()
    div_container.dataset.server_id = data.server_id
    div_container.dataset.done = false

    return div_container
}

function create_error_box(server_id) {
    const box_div = document.createElement("div")
    box_div.className = "error-container round-border shadow"
    
    const error_p = document.createElement("p")
    error_p.id = "error_" + server_id

    box_div.appendChild(error_p)

    return box_div
}

function create_inline_text(msg1, msg2, id="") {
    const inline_div_container = document.createElement("div")
    inline_div_container.className = "inline-text-container"

    const p_1 = document.createElement("p")
    p_1.innerText = msg1
    
    const p_2 = document.createElement("p")
    p_2.innerText = msg2
    p_2.id = id

    inline_div_container.appendChild(p_1)
    inline_div_container.appendChild(p_2)

    return inline_div_container
}

function create_port_item() {
    const item = document.createElement("div")
    item.className = "port-list-item round-border"
    item.innerHTML = `
    <div class="inline-text-container">
        <p title="The port to be used on the physical machine">Host port:</p>
        <input name="host_port" type="number" title="The port to be used on the physical machine" required>
    </div>
    <div class="inline-text-container">
        <p title="The port that the server uses">Server port:</p>
        <input name="server_port" type="number" title="The port that the server uses" required>
    </div>
    <div class="inline-text-container">
        <p>Port type:</p>
        <select name="port_type" title="The port type, leave it as TCP if you're not sure">
            <option>TCP</option>
            <option>UDP</option>
        </select>
    </div>`

    const item_button = document.createElement("button")
    item_button.className = "circle-button remove"
    item_button.innerHTML = "<p>-</p>"
    item_button.type = "button"

    item_button.addEventListener("click", (event) => {
        item.remove()
        form_container.style.height = "auto"
        form_container.style.height = parent_element.style.height = `${form_container.scrollHeight}px`
    })

    item.appendChild(item_button)

    return item
} 

function update_timestamps() {
    const timestamp = Date.now()

    for (const child of job_queue.children) {
        const c_done = child.dataset.done === "true"

        if (c_done) continue

        const div_timestamp = child.dataset.timestamp
        const elapsed_time_div = document.getElementById("start_" + child.dataset.server_id)

        elapsed_time_div.innerText = Math.floor((timestamp - div_timestamp) / 1000) + "s"
    }
}

function toggle_input(listen_id, toggle_ids) {
    // toggles the toggle inputs based on the listen id
    let listen_element = document.getElementById(listen_id)
    let toggle_elements = []

    for (let id of toggle_ids) {
        toggle_elements.push(document.getElementById(id))
    }

    listen_element.addEventListener("change", (e) => {
        for (let toggle_element of toggle_elements) {
            toggle_element.disabled = !toggle_element.disabled
            toggle_element.required = !toggle_element.required
        }
    })
}

function update_slider_output(slider_id, unit) {
    // updates the number on the slider while its being used
    let slider_element = document.getElementById(slider_id)
    let bubble = document.getElementById("out_"+slider_id)

    slider_element.addEventListener("input", (e) => {
        let percent_value = calculate_slider_position(slider_element)

        bubble.textContent = slider_element.value+unit
    })
}

function calculate_slider_position(slider) {
    return (slider.value - slider.min) / (slider.max - slider.min) * 100
}

PORT_LIST.appendChild(create_port_item())
form_container.style.height = "auto"
form_container.style.height = parent_element.style.height = `${form_container.scrollHeight}px`

toggle_input("steam_server", ["steam_id", "launch_opt", "install_opt"])

update_slider_output("cpu_limit", " Cores")
update_slider_output("ram_limit", "GB")

setInterval(() => {
    update_timestamps()
}, 500);