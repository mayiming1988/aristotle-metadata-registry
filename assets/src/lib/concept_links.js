import axios from 'axios'
import 'bootstrap/js/tooltip.js'

function fetchDescription() {
    let desc = $(this).attr('data-description')
    if (desc) {
        return desc
    } else {
        return 'Loading...'
    }
}

export function initConceptLinks() {
    $(document).ready(function() {
        $('a.aristotle-concept-link').tooltip({
            title: fetchDescription,
            placement: 'bottom'
        })
    })
}
