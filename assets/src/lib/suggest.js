// Fuction to initialize suggest name buttons used in item editors
export function initSuggest() {
    let wrappers = document.querySelectorAll('.suggest_name_wrapper')
    // For each suggest name wrapper
    for (let wrapper of wrappers) {
        let button = wrapper.querySelector('button')
        let input = wrapper.querySelector('input')
        // Make sure the buton and input exist
        if (button !== null && input !== null) {
            // Add click listener
            button.addEventListener('click', () => {
                let suggest_fields = button.getAttribute('data-suggest-fields').split(',')
                let separator = button.getAttribute('data-separator')
                let names = []
                for (let field of suggest_fields) {
                    let select = document.getElementById('id_' + field)
                    // If select was found and is a select element
                    if (select !== null && select.tagName == 'SELECT') {
                        // Get option element
                        let option = select.options[select.selectedIndex]
                        // If options value is not blank
                        if (option.value != "") {
                            names.push(option.innerText)
                        }
                    }
                }
                input.value = names.join(separator)
            })
        }
    }
}
