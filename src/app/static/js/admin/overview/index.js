// get all running available servers 
// create the "cards" for each
import setup_graph_updates from "./configure_graphs.mjs"
import {syncCanvasSize} from "../../modules/graph.mjs"

const CONTAINER_LIST = document.getElementById("main-content")
const GRAPH_TYPES = ["cpu", "ram"]
// , "upload", "download"

async function get_all_servers() {
    let data = await fetch("/api/container/all", {
        method: "GET"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("SERVER NOT OK:(")
        }
        return response.json()
    })

    // contains launch options for each server
    let all_graphs = extract_data(data.message)

    if (!all_graphs.servers.length) {
        return null
    }

    return all_graphs
}

function setup_server_containers(server_name) {
    let outer_container = document.createElement("div")
    outer_container.className = "content-container shadow round-border"
    outer_container.id = server_name
    
    let image_container = document.createElement("div")
    image_container.className = "container-image"

    let gradient = document.createElement("div")
    gradient.className = "image-gradient"
    image_container.appendChild(gradient)

    let img = document.createElement("img")
    img.src = `/static/images/${server_name}.jpg`
    
    image_container.appendChild(img)

    outer_container.appendChild(image_container)

    for (let graph_name of GRAPH_TYPES) {
        let graph_container = document.createElement("div")
        graph_container.className = "graph-container"

        let graph_title_container = document.createElement("div")
        graph_title_container.className = "graph-title-container"
        
        let graph_title_inner_container = document.createElement("div")

        let graph_title = document.createElement("p")
        graph_title.textContent = server_name + " " + graph_name
        
        let graph_line = document.createElement("div")
        graph_line.className = "divider"
        
        graph_title_inner_container.appendChild(graph_title)
        graph_title_inner_container.appendChild(graph_line)

        graph_title_container.appendChild(graph_title_inner_container)
        
        let graph = document.createElement("canvas")
        graph.id = server_name + "_" + graph_name
        graph.className = "graph"
        syncCanvasSize(graph)

        graph_container.appendChild(graph_title_container)
        graph_container.appendChild(graph)
        outer_container.appendChild(graph_container)
    }
    CONTAINER_LIST.appendChild(outer_container)
}

function extract_data(response) {
    return response
}

async function main() {
    let all_graphs = await get_all_servers()

    if (!all_graphs) return

    for (let server_name of all_graphs.servers) {
        setup_server_containers(server_name)
    }

    setup_graph_updates(all_graphs.servers, GRAPH_TYPES)
}

main()