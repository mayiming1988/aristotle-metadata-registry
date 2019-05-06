import {initCore} from 'src/lib/init.js'

import 'src/styles/taggle.css'
import 'src/styles/aristotle.dashboard.less'

initCore();

let selectAllCheckbox = document.getElementById('select_all_checkbox');
selectAllCheckbox.addEventListener("change", function () {
    toggle_all_checkboxes(this);
    show_select_all_div();
});

function toggle_all_checkboxes(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source) {
            checkboxes[i].checked = source.checked;
        }
    }
}

function show_select_all_div() {
    var select_all = document.getElementById('select-all-div')

    if (select_all.style.display == 'block') {
        select_all.style.display = 'none';
    }
    else {
        select_all.style.display = 'block';
    }

}