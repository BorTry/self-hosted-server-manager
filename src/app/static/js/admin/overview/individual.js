import draw_points, {sync_canvas_size} from "../../modules/graph.mjs"

const CONTAINER_LIST = document.getElementById("main-content")
const SERVER_NAMES = []
const GRAPH_TYPES = ["cpu", "ram", "upload", "download"]
const MIN_TIME_DIFF = 1.4

var METRICS = []
var TIME_BETWEEN = 15 // default

async function get_data() {
    METRICS = await fetch("/api/admin/performance_metrics/"+SERVER_NAME, {
        method: "GET"
    }).then(response => {
        if (!response.ok) {
            throw new Error("SERVER NOT OK:(")
        }
        return response.json()
    });
    TIME_BETWEEN = METRICS["time_between"]||15
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
                ordered_points.push([i, {"cpu":0, "ram":0, "upload":0, "download":0}])
                i++
            }
        } else {
            ordered_points.push([i, {
                "cpu": Math.ceil(entry.cpu) / 100,
                "ram": Math.ceil(entry.ram) / 100,
                "upload": Math.ceil(entry.upload || 0) / 100,
                "download": Math.ceil(entry.download || 0) / 100
            }])
            i++
        }
    }

    return ordered_points
}

function update_graphs(graph_name, types) {  
    let ordered_points = order_by_date(METRICS)

    for (let type of types) {
        let canvas = document.getElementById(type)
        
        draw_points(canvas, ordered_points, (x) => x[type])
    }
}

export default async function setup_graph_updates(graph_name, types) {
    await get_data() // gets the "time_between"
    update_graphs(graph_name, types)

    setInterval(get_data, TIME_BETWEEN * 1000)
    setInterval(update_graphs, 1000, graph_name, types)
    
    window.onresize = () => {
        for (let type of types) {
            let canvas = document.getElementById(type)
            
            sync_canvas_size(canvas)
        }

        update_graphs(graph_name, types)
    }
}

async function main() {
    let graphs = document.getElementsByClassName("graph")

    for (let graph of graphs) {
        sync_canvas_size(graph)
    }

    setup_graph_updates(SERVER_NAME, GRAPH_TYPES)
}

main()