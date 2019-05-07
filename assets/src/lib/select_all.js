// To add the gmail-style select all button to a bulk_action page:
    // 1. import {initSelectAll} from "src/lib/select_all"
    // 2. initSelectAll()
    // 3. Add {{page}}.js to webpack
    // 4. Add total_query_size context to your view

export function initSelectAll() {

    let selectAllCheckbox = document.getElementById('select-all-checkbox');
    selectAllCheckbox.addEventListener("change", function () {
        toggle_all_checkboxes(this);
        if (document.getElementById('select-all-checkbox').checked) {
            show_initial_div()
        }
        else {
            // Checkbox is not checked
            hide_initial_div()
        }
    });

    let selectAllQuerysetButton = document.getElementById("select-all-queryset-button")
    selectAllQuerysetButton.addEventListener("click", function () {
        select_all_queryset();
    });
}

function toggle_all_checkboxes(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source) {
            checkboxes[i].checked = source.checked;
        }
    }
    document.getElementById("all_in_queryset").checked = false;
}

function show_initial_div() {
    let initial = document.getElementById('initial-div')
    initial.style.display = 'block';
}

function hide_initial_div() {
    let initial = document.getElementById('initial-div')
    initial.style.display = 'none';

}

function select_all_queryset() {
    swap_divs();

    document.getElementById("clear-selections-button").addEventListener("click",
        function () {
            clear_selections(this);
    });
    document.getElementById("all_in_queryset").checked = true;
}
function clear_selections(source) {
    hide_select_all_div()
    hide_initial_div()
    toggle_all_checkboxes(source)
}

function swap_divs() {
    let select_all = document.getElementById('select-all-div')

    if (select_all.style.display == 'block') {
        // If div is displayed, hide it
        select_all.style.display = 'none';
    } else {
        // Show it
        select_all.style.display = 'block';
    }
    let initial_div = document.getElementById('initial-div')

    if (initial_div.style.display == 'block') {
        initial_div.style.display = 'none';
    } else {
        initial_div.style.display = 'block'
    }
}

function hide_select_all_div() {
    let select_all = document.getElementById('select-all-div')
    select_all.style.display = 'none';
}