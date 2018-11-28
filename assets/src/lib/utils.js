export function capitalize(text) {
    let first = text.charAt(0)
    return first.toUpperCase() + text.slice(1)
}

export function buildElement(tagName, attrs, text) {
    let elem = document.createElement(tagName)
    for (let item of Object.entries(attrs)) {
        elem.setAttribute(item[0], item[1])
    }
    if (text != undefined) {
        elem.appendChild(document.createTextNode(text))
    }
    return elem
}
