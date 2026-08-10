const dropdown_titles = document.getElementsByClassName("dropdown-title")
const dropdown_menus = []
const parent_element = document.getElementById("dropdown-menus")

var last_size = Infinity
var last_element = null
var last_title = null

for (let title of dropdown_titles) {
    dropdown_menus.push(document.getElementById(title.id + "_dropdown"))

    title.addEventListener("click", (e) => {
        let current_drop_down = document.getElementById(title.id + "_dropdown")
        let is_collapsed = current_drop_down.style.height === ""

        title.style.backgroundColor = is_collapsed = "var(--secondary)" 

        if (last_element) {
            last_element.style.position = "absolute"
            last_element.style.zIndex = 0

            // this has to be set if last_element is set
            last_title.style.backgroundColor = "var(--main)"
    
            if (last_size > current_drop_down.scrollHeight) {
                last_element.style.height = ""

            } else if (last_element) {
                let tmp_el = last_element
                setTimeout(() => {
                    tmp_el.style.height = ""
                }, 0.75 * 1000);
            }
        }

        current_drop_down.style.zIndex = 1

        requestAnimationFrame(() => {
            current_drop_down.style.height = parent_element.style.height = is_collapsed ? `${current_drop_down.scrollHeight}px` : ""
            current_drop_down.style.position = is_collapsed ? "relative" : "absolute"
        })

        last_element = current_drop_down
        last_size = current_drop_down.scrollHeight
        last_title = title
    })
}

const chosen_title = dropdown_titles[0]
const open_menu = document.getElementById(chosen_title.id + "_dropdown")

chosen_title.style.backgroundColor = "var(--secondary)" 

open_menu.style.height = parent_element.style.height = `${open_menu.scrollHeight}px`
open_menu.style.position =  "relative"

last_size = open_menu.scrollHeight
last_element = open_menu
last_title = chosen_title