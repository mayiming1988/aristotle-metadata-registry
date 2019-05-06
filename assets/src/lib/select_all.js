export function initSelectAll() {
    let selectAllCheckbox = document.getElementById('select-all-checkbox');
    selectAllCheckbox.addEventListener("change", function () {
        toggle_all_checkboxes(this);
        toggle_select_all_div();
    });

    let selectAllQuerysetButton = document.getElementById("select-all-queryset-button")
    selectAllQuerysetButton.addEventListener("click", function () {
        select_all_queryset()
    });

    var initialText = document.getElementById('select-all-div').innerHTML;

}


function toggle_all_checkboxes(source) {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i] != source) {
            checkboxes[i].checked = source.checked;
        }
    }
}

function toggle_select_all_div() {
    var select_all = document.getElementById('select-all-div')

    if (select_all.style.display == 'block') {
        select_all.style.display = 'none';
    } else {
        select_all.style.display = 'block';
    }

}

function select_all_queryset() {
    let length_queryset = document.getElementById('select-all-queryset-button').getAttribute('data-total-queryset');

    let markup = `
        All of your ${length_queryset} favourites have been selected 
        <button class="btn btn-outline btn-outline-info" id="clear-selections-button" type="reset">Clear selections</button>
        `;

    document.getElementById("select-all-div").innerHTML = markup;

    document.getElementById("clear-selections-button").
        addEventListener("click", function () {
            clear_selections();
    });

    // Select the hidden queryset checkbox
    document.getElementById("all_in_queryset").checked = true;
}

function clear_selections() {
    toggle_select_all_div();
    document.getElementById("select-all-div").innerHTML = '';

}