// Rendered on user base template
import init, { initWidgets } from '../lib/init.js'

import '../styles/aristotle.dashboard.less'

init()

$(document).ready(function() {
    $('.modal').on('loaded.bs.modal', function() {
        initWidgets()
    })
})
