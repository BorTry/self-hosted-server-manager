const dropdown_menues = document.getElementsByClassName("dropdown-container")

for (let menu of dropdown_menues) {
    menu.addEventListener("click", (e) => {
        if (!menu.className.includes("active")) {
            menu.className = menu.className+" active"
        } else {
            menu.className = menu.className.replace("active", "")
        }
    })
}