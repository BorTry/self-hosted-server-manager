const dropdown_titles = document.getElementsByClassName("dropdown-title")

for (let title of dropdown_titles) {
    title.addEventListener("click", (e) => {
        let dropdown_menu = title.parentElement
        if (!dropdown_menu.className.includes("active")) {
            dropdown_menu.className = dropdown_menu.className+" active"
        } else {
            dropdown_menu.className = dropdown_menu.className.replace(" active", "")
        }
    })
}