import settings from 'src/settings.json'
import request from 'src/lib/request.js'
import 'bootstrap/js/tooltip.js'

function fetchDefinition(id) {
    let apiurl = '/api/v4/item/' + id

    let promise = request('get', apiurl, {})
    
    // Return a new promise that returns the definition or an error message
    return promise.then((result) => {
        return result.data['short_definition']
    }).catch((error) => {
        if (error.response) {
            let status_code = error.response.status
            // If unauthorized or permission denied
            if (status_code === 401 || status_code === 403) {
                return settings.no_permission_msg
            }
        }
        // Generic fail message
        return settings.not_found_msg
    })
}

function getToolText() {
    let desc = $(this).attr('data-definition')
    if (desc) {
        return desc
    } else {
        let loadingattr = $(this).attr('data-loading')
        if (!loadingattr) {
            $(this).attr('data-loading', '1')
            fetchDefinition($(this).attr('data-aristotle-concept-id'))
            .then((defn) => {
                $(this).attr('data-definition', defn)
                $(this).attr('data-loading', '')
                $(this).tooltip('show')
            })
        }
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
