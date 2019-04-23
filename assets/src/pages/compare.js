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

function save_current_state() {
    // Get the visibility states
    var visibilitySelects = document.getElementsByClassName('visibility-select');
    // Create a variable
}

function enable_editing() {
    var visibilitySelects = document.getElementsByClassName('visibility-select');
    for (let select of visibilitySelects) {
        select.disabled = false;
    }
    var saveVisibilityButton = document.getElementById('save-visibilities-button');
    saveVisibilityButton.disabled = false;
}

function update_visibilities() {
    let idToVisibility = {};

    let objectElement = document.getElementById("change-history")
    let objectId = objectElement.getAttribute("data-object-id");

    let visibilitySelects = document.getElementsByClassName('visibility-select');

    // Iterate through selections

    // TODO: only get changed to minimize database hitting
    for (let element of visibilitySelects) {
        let value = element.options[element.selectedIndex].value;

        let visibility = {
            'visibility': value
        }

        let id = element.getAttribute("data-version-id");
        idToVisibility[id] = visibility;
    }


    // TODO : move to getting url from data element set by {% url %}
    let base_url = "/api/v4/item/" + objectId + "/update-permission/";

    let urls = new Array();

    for (let id in idToVisibility) {
        let url = base_url + id + "/";
        let visibilityPermissions  = idToVisibility[id]
        let params = ''
        request("PATCH", url, visibilityPermissions, params)
    }
    addHeaderMessage('Saving performed sucesfully');
}

