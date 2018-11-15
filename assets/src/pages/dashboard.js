// Rendered on user base template
import init, { initWidgets }from 'src/lib/init.js'

import 'src/styles/aristotle.dashboard.less'

init()

$(document).ready(function() {
    $('.modal').on('loaded.bs.modal', function() {
        initWidgets()
    })
})
