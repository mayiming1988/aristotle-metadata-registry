import init from 'src/lib/init.js'

import request from 'src/lib/request.js'
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

init();
initMessages();

let addButtons = document.getElementsByClassName('promote-button');

for (let button of addButtons) {
      button.addEventListener('click', promote_to_items);
    }

function promote_to_items() {
    // From the
    let tableElement = document.getElementById('item-table')
    let url = tableElement.getAttribute("data-promote-url")

    let body = {"concept_id" : this.id}

    let params = ''
    request("PUT", url, body, params).then(
        () => {
            addHeaderMessage("Promoting item was succesful!");
            document.getElementById(this.id).innerText = "Promoted";
            document.getElementById(this.id).disabled = true;
        });
}