// Capitalizes the first character in a string
export function capitalize(text) {
    let first = text.charAt(0)
    return first.toUpperCase() + text.slice(1)
}

// Uncamel cases a string
export function unCamel(text) {
    let space_text = text.replace(/([a-z0-9])([A-Z])/g, (match, lc, uc) => {
        return [lc, uc].join(' ')
    })
    return space_text
}

// Flattens a list of objects to a list of one attribute of the objects
export function flatten(list, attr) {
    let newlist = []
    for (let item of list) {
        newlist.push(item[attr])
    }
    return newlist
}
