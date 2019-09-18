import init, { initWidgets } from 'src/lib/init.js'
import 'src/styles/ra.css'

init()

// Load widgets on modal load (needed for memebers modal
$(document).ready(function() {
    $('.modal').on('loaded.bs.modal', function() {
        initWidgets()
    })
})
