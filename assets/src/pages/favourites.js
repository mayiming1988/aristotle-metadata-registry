import {initCore} from 'src/lib/init.js'

import 'src/styles/taggle.css'
import 'src/styles/aristotle.dashboard.less'

initCore();

let selectAllCheckbox = document.getElementById("select_all_checkbox")
selectAllCheckbox.addEventListener("change", function () {
        toggle_all_checkboxes(this);
});

function toggle_all_checkboxes(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source)
            checkboxes[i].checked = source.checked;
    }

}

