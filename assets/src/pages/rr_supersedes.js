import { initCore } from 'src/lib/init.js'
import { initDAL } from 'src/lib/dal_simple_init.js'
import initFormset from 'src/lib/formset.js'

function get_url(element) {
    let id = element.attr('id')
    let newer_item_select = document.getElementById(id.replace('older', 'newer'))
    let url = element.attr('data-autocomplete-light-url')
    return function() {
        if (newer_item_select !== null) {
            let selected = newer_item_select.options[newer_item_select.selectedIndex]
            if (selected !== null && selected.hasAttribute('data-label')) {
                return url + selected.getAttribute('data-label').replace('.', '-')
            }
        }
        return url
    }
}

initCore()
initDAL(get_url)
initFormset(get_url)
