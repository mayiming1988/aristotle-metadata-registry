import init from 'src/lib/init.js'

import request from 'src/lib/request.js'
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

init();
initMessages();

let removeButtons = document.getElementsByClassName('remove-button');

Array.from(removeButtons).forEach(function(element) {
      element.addEventListener('click', remove_from_items);
    });

function remove_from_items() {
    let tableElement = document.getElementById('item-table')
    let url = tableElement.getAttribute("data-remove-url")

    let body = {"concept_id" : this.id}

    let params = ''
    request("PUT", url, body, params).then(
        () => {
            addHeaderMessage("Removing item was succesful!");
            document.getElementById(this.id).innerText = "Removed";
            document.getElementById(this.id).disabled = true;
        });
}