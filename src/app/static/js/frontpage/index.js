import build_request_form from "./card_factory.mjs"
import update_gauge from "../modules/gauge.mjs"

var RUNNING_SERVERS = []
var ALL_SERVERS = []
const PREV_STATES = {}

// set an interval to get server data
setInterval(async function() {
    await change_live_servers()
}, 3 * 1000)

// find out which servers can be ran
async function build_server_list() {
    let servers = document.getElementsByClassName("server-container")

    for (const server_element of servers) {
        ALL_SERVERS.push(server_element.id)
    }

    for (let server_name of ALL_SERVERS) {
        build_request_form(server_name)
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

    let server_stats = data.message

    for (let server_name of ALL_SERVERS) {
        let is_online = Object.hasOwn(server_stats, server_name)
        let server_entry = server_stats[server_name]

        if (PREV_STATES[server_name] === is_online) continue

        PREV_STATES[server_name] = is_online

        change_server_status(server_name, is_online)
        update_gauge(`cpu-gauge-${server_name}`, server_entry ? server_entry.cpu : 0)
        update_gauge(`ram-gauge-${server_name}`, server_entry ? server_entry.ram : 0)
    }
}

function change_server_status(name, online=true) {
    let image_con = document.getElementById(name)
    image_con.style.borderColor = online ? "var(--online)" : "var(--offline)"
}

async function main() {
    await build_server_list()
    await change_live_servers()
}

main()