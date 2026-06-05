const ADD_SERVER_FORM = document.getElementById("add_server_form")
const SERVER_STREAM = new EventSource("/api/admin/add_container")

SERVER_STREAM.addEventListener("update", (event) => {
    console.log(event.data)
})

SERVER_STREAM.addEventListener("close", (event) => {
    SERVER_STREAM.close()
})

ADD_SERVER_FORM.addEventListener("submit", (e) => {
    e.preventDefault();
        
    let formData = new FormData(e.target);

    fetch("/api/admin/add_container", {
        method: "POST",
        body: formData
    })
})

function toggle_input(listen_id, toggle_ids) {
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

toggle_input("restrict_ports", ["port_type"])
toggle_input("steam_server", ["steam_id", "launch_opt", "install_opt"])

update_slider_output("cpu_limit", " Cores")
update_slider_output("ram_limit", "GB")