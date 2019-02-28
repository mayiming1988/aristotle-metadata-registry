// You're a wizard harry
import { initCore, initWidgets } from 'src/lib/init.js'

import 'src/styles/aristotle.wizard.less'

initCore()
initWidgets()


// Display a prompt when the user navigates away from the page
function handleUnload(event) {
    event.preventDefault()
    // Most newer browsers don't display this message and use a general message instead
    event.returnValue = 'Are you sure you want to leave? Data you have entered may not be saved'
}

// add event
window.addEventListener('beforeunload', handleUnload)

// remove unload event when clicking a button
let buttons = document.querySelectorAll('button')
for (let button of buttons) {
    button.addEventListener('click', () => {
        // On button click remove the before unload listener
        window.removeEventListener('beforeunload', handleUnload)
    })
}
