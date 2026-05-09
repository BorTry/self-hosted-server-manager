var RUNNING_SERVERS = []

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

    console.log(data.message.servers)

    // contains launch options for each server
    let all_servers = extract_data(data.message)

    if (!all_servers.servers.length) {
        return
    }

    for (let server_name of all_servers.servers) {
        create_server_card(server_name, all_servers.launch_options)
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

    let all_servers = extract_data(data.message)

    // turn all server-listing red if none are running
    if (!all_servers) {
        if (!RUNNING_SERVERS.length) return

        for (let server_name of RUNNING_SERVERS) {
            change_server_status(server_name, false)
            update_gauge(`cpu-gauge-${server_name}`, 0)
            update_gauge(`ram-gauge-${server_name}`, 0)
        }
        return
    }

    // update the ram and cpu gauges for each server
    for (let usage of all_servers) {
        update_gauge(`cpu-gauge-${usage.name}`, usage.cpu)
        update_gauge(`ram-gauge-${usage.name}`, usage.ram)
    }

    // turn "all server" items green if none are recorded as running
    if (!RUNNING_SERVERS.length) {
        for (let server_name of all_servers) {
            change_server_status(server_name.name)
            RUNNING_SERVERS.push(server_name.name)
        }

        return
    }

    let tmp_arr = []

    // Change the servers to be red:)
    for (let server_name of all_servers) {
        let index = RUNNING_SERVERS.indexOf(server_name.name)

        if (index < 0) {
            change_server_status(server_name.name)
            continue
        }
        
        change_server_status(server_name.name)
        RUNNING_SERVERS.splice(index, 1)
    }

    // Change the servers to be red:)
    for (let server_name of RUNNING_SERVERS) {
        change_server_status(server_name, false)
        update_gauge(`cpu-gauge-${server_name}`, 0)
        update_gauge(`ram-gauge-${server_name}`, 0)
    }

    RUNNING_SERVERS.length = 0

    for (let server_name of all_servers) {
        RUNNING_SERVERS.push(server_name.name)
    }
}

function change_server_status(name, online=true) {
    let el = document.getElementById(name)
    let image_con = el.getElementsByClassName("server-item-image")[0]
    image_con.style.borderColor = online ? "var(--online)" : "var(--offline)"
}

function extract_data(response) {
    // flip the order of " and ' ...
    return response
    return JSON.parse(response)
}

async function main() {
    await build_server_list()
    await change_live_servers()
}

main()