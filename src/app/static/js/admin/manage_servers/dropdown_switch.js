const dropdown_titles = document.getElementsByClassName("dropdown-title")
const dropdown_menus = []
const parent_element = document.getElementById("dropdown-menus")

for (let title of dropdown_titles) {
    dropdown_menus.push(document.getElementById(title.id + "_dropdown"))

    title.addEventListener("click", (e) => {
        let current_drop_down = document.getElementById(title.id + "_dropdown")
        let is_collapsed = current_drop_down.style.height === ""

        title.style.backgroundColor = is_collapsed = "var(--secondary)" 

        for (const element of dropdown_menus) {            
            element.style.height = ""
            element.style.zIndex = 0
            element.style.position = "absolute"
        }

        for (const other_title of dropdown_titles) {          
            if (other_title.id === title.id) continue  
            other_title.style.backgroundColor = "var(--main)"
        }

        current_drop_down.style.zIndex = 1

        requestAnimationFrame(() => {
            current_drop_down.style.height = parent_element.style.height = is_collapsed ? `${current_drop_down.scrollHeight}px` : ""
            current_drop_down.style.position = is_collapsed ? "relative" : "absolute"
        })
    })
}

const chosen_title = dropdown_titles[0]
const open_menu = document.getElementById(chosen_title.id + "_dropdown")

chosen_title.style.backgroundColor = "var(--secondary)" 

open_menu.style.height = parent_element.style.height =  `${open_menu.scrollHeight}px`
open_menu.style.position =  "relative"