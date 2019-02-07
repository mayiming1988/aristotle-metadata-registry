import { initCore, initWidgets } from 'src/lib/init.js'

initCore()

// Load widgets on modal load (needed for memebers modal
$(document).ready(function() {
    $('.modal').on('loaded.bs.modal', function() {
        initWidgets()
    })
})
