import { initCore, initWidgets } from 'src/lib/init.js'
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'

import 'src/styles/diff.css'
import 'src/styles/aristotle.comparisons.less'

initCore();
initWidgets();
initMessages();


document.getElementById('compare').addEventListener("click", go_to_compare);

function go_to_compare(event) {
    let firstItemSelect = document.querySelector('select[name="item_a"]');
    let secondItemSelect = document.querySelector('select[name="item_b"]');

    if (firstItemSelect === null || secondItemSelect === null) {
        return null
    }

    if (firstItemSelect.value === secondItemSelect.value) {
        // You can't compare the same version
        addHeaderMessage("You can't compare an item with itself!");
        event.preventDefault();
    }
}
