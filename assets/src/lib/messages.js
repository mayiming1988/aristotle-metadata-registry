function clearMessages() {
    $('#messages-row').find('ul').html('')
}

function clearAndHideMessages() {
    clearMessages()
    $('#messages-row').attr('hidden', '')
}

export function addHeaderMessage(message) {
    clearMessages()
    var row = $('#messages-row')
    row.find('.alert').removeAttr('hidden')
    var message_list = row.find('ul')

    var element = $('<li>', {text: message})
    message_list.append(element)
}

export function initMessages() {
    $('#messages-row').find('.close').click(clearAndHideMessages)
}
