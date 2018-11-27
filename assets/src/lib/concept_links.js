import request from 'src/lib/request.js'
import 'bootstrap/js/tooltip.js'

function fetchDefinition(id) {
    let apiurl = '/api/v4/item/' + id

    let promise = request('get', apiurl, {})
    
    // Return a new promise that returns the definition
    return promise.then((result) => {
        return result.data['short_definition']
    })
}

function getToolText() {
    let desc = $(this).attr('data-definition')
    if (desc) {
        return desc
    } else {
        fetchDefinition($(this).attr('data-aristotle-concept-id'))
        .then((defn) => {
            $(this).attr('data-definition', defn)
            $(this).tooltip('show')
        })
        return 'Loading...'
    }
}

export function initConceptLinks() {
    $(document).ready(function() {
        $('a.aristotle-concept-link').tooltip({
            title: getToolText,
            trigger: 'hover',
            placement: 'bottom'
        })
    })
}
