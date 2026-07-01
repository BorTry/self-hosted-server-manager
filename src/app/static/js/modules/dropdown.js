const dropdown_titles = document.getElementsByClassName("dropdown-title")

for (let title of dropdown_titles) {
    title.addEventListener("click", (e) => {
        let dropdown_menu = title.parentElement

        console.log(dropdown_menu.style.height)

        requestAnimationFrame(() => {
            if (dropdown_menu.style.height === "") {
                dropdown_menu.style.height = `${dropdown_menu.scrollHeight}px`
            } else {
                dropdown_menu.style.height = ""
            }
        })

        /*if (!dropdown_menu.className.includes("active")) {
            dropdown_menu.className = dropdown_menu.className+" active"
        } else {
            dropdown_menu.className = dropdown_menu.className.replace(" active", "")
        }*/
    })
}