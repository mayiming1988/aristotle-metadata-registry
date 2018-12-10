export function capitalize(text) {
    let first = text.charAt(0)
    return first.toUpperCase() + text.slice(1)
}

export function flatten(list, attr) {
    // Flattens a list of objects
    let newlist = []
    for (let item of list) {
        newlist.push(item[attr])
    }
    return newlist
}
