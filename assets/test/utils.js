export function addMessageRow(root_element) {
  var div = document.createElement("div")
  div.setAttribute('id', 'messages-row')
  div.setAttribute('class', 'row')

  var alert = document.createElement('div')
  alert.setAttribute('class', 'alert alert-info')
  alert.setAttribute('hidden', '')

  div.appendChild(alert)

  var ul = document.createElement('ul')
  ul.setAttribute('class', 'messages')

  alert.appendChild(ul)

  root_element.appendChild(div)
    
}
