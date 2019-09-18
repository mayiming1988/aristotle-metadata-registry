import init from 'src/lib/init.js'
import request from 'src/lib/request.js'

import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

import openClose from '@/reviews/openClose.vue'
import renderComponents from 'src/lib/renderComponents.js'

init();
initMessages();

renderComponents({
    'open-close-approved': openClose
})

let addButtons = document.querySelectorAll('.promote-button');

for (let button of addButtons) {
      button.addEventListener('click', promote_to_items);
    }

function promote_to_items() {
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
