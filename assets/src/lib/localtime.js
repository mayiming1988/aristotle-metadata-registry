import moment from 'moment'
const default_format = 'MMMM Do YYYY'

export function initTime() {
    $('time').each(function() {
        let node = $(this)
        let dt = node.attr('datetime')
        let format = node.attr('data-format')
        if (format === undefined) {
            format = default_format
        }
        let local = moment(dt).format(format)
        node.text(local)
        node.attr('title', local)
    })
}
