import init from 'src/lib/init.js'

import 'src/styles/aristotle.compare.less'
import request from 'src/lib/request.js'
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

init();
initMessages();

document.getElementById('edit-visibilities-button').addEventListener("click", enable_editing);
document.getElementById('save-visibilities-button').addEventListener("click", update_visibilities);

document.getElementById('compare').addEventListener("click", go_to_compare);

function enable_editing() {
    var visibilitySelects = document.getElementsByClassName('visibility-select');
    for (let select of visibilitySelects) {
        select.disabled = false;
    }
    var saveVisibilityButton = document.getElementById('save-visibilities-button');
    saveVisibilityButton.disabled = false;
}

function update_visibilities() {
    let objectElement = document.getElementById("change-history");
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

function go_to_compare() {
    let compareButton = document.getElementById('compare');

    let base_url = compareButton.getAttribute('data-compare-url');

    let firstVersionRadioButton = document.querySelector('input[name="version_id1"]:checked');
    let secondVersionRadioButton = document.querySelector('input[name="version_id2"]:checked');

    if (firstVersionRadioButton === null || secondVersionRadioButton === null) {
        return null
    }
    let firstVersionId =  firstVersionRadioButton.value;
    let secondVersionId = secondVersionRadioButton.value;

    if (firstVersionId === secondVersionId) {
        // You can't compare the same version
        addHeaderMessage("You can't compare a version with itself!");
        return null
    }

    let url = base_url + `?v1=${firstVersionId}&v2=${secondVersionId}`
    // Redirect to URL
    window.location.href = url



}
