import build_request_form from "./card_factory.mjs"
import update_gauge from "../modules/gauge.mjs"

var RUNNING_SERVERS = []
var ALL_SERVERS = []

// set an interval to get server data
setInterval(async function() {
    await change_live_servers()
}, 3 * 1000)

// find out which servers can be ran
async function build_server_list() {
    let data = await fetch("/api/container/all", {
        method: "GET"
    })
    .then( response => {
        if (!response.ok) {
            throw new Error("SERVER NOT OK:(")
        }
        return response.json()
    })

    let servers = extract_data(data.message)

    ALL_SERVERS = servers.all_servers

    if (!servers) {
        return
    }

    for (let server_name of servers.all_servers) {
        build_request_form(server_name, servers.launch_opts)
    }
}

// find out which servers are running
async function change_live_servers() {
    let data = await fetch("/api/container/all/running", {
        method: "GET"
    })
    .then( response => {
        if (!response.ok) {
            throw new Error("SERVER NOT OK:(")
        }
        return response.json()
    })

    let server_stats = extract_data(data.message)

    for (let server_name of ALL_SERVERS) {
        let is_online = Object.hasOwn(server_stats, server_name)
        let server_entry = server_stats[server_name]

        change_server_status(server_name, is_online)
        update_gauge(`cpu-gauge-${server_name}`, is_online ? server_entry.cpu : 0)
        update_gauge(`ram-gauge-${server_name}`, is_online ? server_entry.ram : 0)
    }
}

function change_server_status(name, online=true) {
    let image_con = document.getElementById(name)
    image_con.style.borderColor = online ? "var(--online)" : "var(--offline)"
}

function extract_data(response) {
    return response
}

async function main() {
    await build_server_list()
    await change_live_servers()
}

main()