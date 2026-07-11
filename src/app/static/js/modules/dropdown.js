const dropdown_titles = document.getElementsByClassName("dropdown-title")

for (let title of dropdown_titles) {
    title.addEventListener("click", (e) => {
        let dropdown_menu = title.parentElement
        let is_collapsed = dropdown_menu.style.height === ""

        dropdown_menu.style.height = "0px"

        requestAnimationFrame(() => {
            if (is_collapsed) {
                dropdown_menu.style.height = `${dropdown_menu.scrollHeight}px`
            } else {
                dropdown_menu.style.height = ""
            }
        })
    })
}