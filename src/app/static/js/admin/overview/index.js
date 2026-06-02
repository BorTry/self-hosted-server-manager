import draw_points, {sync_canvas_size} from "../../modules/graph.mjs"

const CONTAINER_LIST = document.getElementById("main-content")
const SERVER_NAMES = []
const GRAPH_TYPES = ["cpu", "ram"]
const MIN_TIME_DIFF = 1.4

var METRICS = []
var TIME_BETWEEN = 15 // default

async function get_data() {
    METRICS = await fetch("/api/admin/performance_metrics", {
        method: "GET"
    }).then(response => {
        if (!response.ok) {
            throw new Error("SERVER NOT OK:(")
        }
        return response.json()
    });
    TIME_BETWEEN = METRICS["time_between"]
}

function order_by_date(points) {
    if (!points) return

    let seconds_since = 0
    let ordered_points = []

    let i = 0

    for (let index = 1; index < points.length; index++) {
        let entry = points[index]
        seconds_since = (Date.parse(entry.time) - Date.parse(points[index - 1].time)) / (1000)

        if ((seconds_since / TIME_BETWEEN) > MIN_TIME_DIFF) {
            for (let it = 0; it < Math.floor(seconds_since / TIME_BETWEEN); it++) {
                ordered_points.push([i, {"cpu":0, "ram":0}])
                i++
            }
        } else {
            ordered_points.push([i, {
                "cpu": Math.ceil(entry.cpu) / 100,
                "ram": Math.ceil(entry.ram) / 100
            }])
            i++
        }
    }

    return ordered_points
}

function update_graphs(graph_names, types) {
    for (let name of graph_names) {
        if (!(name in METRICS)) continue
        
        let ordered_points = order_by_date(METRICS[name])
        
        for (let type of types) {
            let canvas = document.getElementById(name + "_" + type)
            
            draw_points(canvas, ordered_points, (x) => x[type])
        }
    }
}

export default async function setup_graph_updates(graph_names, types) {
    await get_data() // gets the "time_between"
    update_graphs(graph_names, types)

    setInterval(get_data, TIME_BETWEEN * 1000)
    setInterval(update_graphs, 1000, graph_names, types)
    
    window.onresize = () => {
        for (let name of graph_names) {
            for (let type of types) {
                let canvas = document.getElementById(name + "_" + type)
                
                sync_canvas_size(canvas)
            }
        }

        update_graphs(graph_names, types)
    }
}

async function main() {
    for (let server_element of CONTAINER_LIST.children) {
        SERVER_NAMES.push(server_element.id)
    }

    let graphs = document.getElementsByClassName("graph")

    for (let graph of graphs) {
        sync_canvas_size(graph)
    }

    setup_graph_updates(SERVER_NAMES, GRAPH_TYPES)
}

main()