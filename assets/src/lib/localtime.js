import moment from 'moment'
const default_format = 'Do MMMM YYYY'

export function initTime() {
    $('time').each(function() {
        let node = $(this)
        let dt = node.attr('datetime')
        let format = node.attr('data-format')
        let from = (node.attr('data-time-from') === 'true')

        if (format === undefined) {
            format = default_format
        }

        // datetime attribute is - if the date has a None value in the backend
        // in this case we just set the text and title to -
        let local = '-'
        if (dt != '-') {
            if (from) {
                // Display value from this datetime to now e.g 4 days ago
                local = moment(dt).fromNow()
            } else {
                // Display datetime
                local = moment(dt).format(format)
            }
        }

        node.text(local)
        node.attr('title', local)
    })
}
