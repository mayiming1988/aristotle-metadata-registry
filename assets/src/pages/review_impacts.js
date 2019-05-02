import init from 'src/lib/init.js'

import request from 'src/lib/request.js'
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

init();
initMessages();
$(document).ready(function() {
    let addButtons = document.getElementsByClassName('promote-button');

    Array.from(classname).forEach(function(element) {
      element.addEventListener('click', myFunction);
    });
});

console.log("ww")

