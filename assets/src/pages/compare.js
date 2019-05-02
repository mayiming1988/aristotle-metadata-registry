import init from 'src/lib/init.js'

import 'src/styles/aristotle.compare.less'
import request from 'src/lib/request.js'
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

init();
initMessages();

$(document).ready(function() {
    document.getElementById('edit-visibilities-button').addEventListener("click", enable_editing);
    document.getElementById('save-visibilities-button').addEventListener("click", update_visibilities);
});

function enable_editing() {
    var visibilitySelects = document.getElementsByClassName('visibility-select');
    for (let select of visibilitySelects) {
        select.disabled = false;
    }
    var saveVisibilityButton = document.getElementById('save-visibilities-button');
    saveVisibilityButton.disabled = false;
}

function update_visibilities() {
    let objectElement = document.getElementById("item-table");
    let url = objectElement.getAttribute("data-update-api-url");

    let visibilitySelects = document.getElementsByClassName('visibility-select');

    // Iterate through selections
    let updatedVisibilities = new Array();
    for (let select of visibilitySelects) {

        let visibility = select.options[select.selectedIndex].value;
        let version_id = select.getAttribute("data-version-id");

        let obj = {
            'version_id': version_id,
            'visibility': visibility
        }

        updatedVisibilities.push(obj);
    }
    let params = ''
    request("POST", url, updatedVisibilities, params).then(
        () => addHeaderMessage("Saving visibilities was successful!"));
}

