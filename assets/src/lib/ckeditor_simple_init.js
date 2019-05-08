/* globals CKEDITOR */
import 'ckeditor/ckeditor.js'
// This import is necessary to include, otherwise the import won't work
import 'ckeditor/plugins/justify/plugin.js'
import  {addPlugins} from 'src/lib/ckeditor_plugins.js'
addPlugins(CKEDITOR)

// Initialize a ckeditor instance config can be provided to function or in data-config attr
export function initCKEditor(config) {
    let textareas = document.querySelectorAll('textarea[data-type=ckeditortype]')
    for (let te of textareas) {
        initCKEditorFromTextarea(te, config)
    }
}

export function initCKEditorFromTextarea(textarea, config) {
    let processed = textarea.getAttribute('data-processed')
    if (processed == 0 || processed == null) {
        // If config not provided use data-config
        if (config === undefined) {
            config = JSON.parse(textarea.getAttribute('data-config'));
        }
        console.log(config)
        console.log(textarea)
        CKEDITOR.replace(textarea, config)
        textarea.setAttribute('data-processed', 1)
    }
}

// ReInitialize ckeditor instances
export function reinitCKEditors(form) {
    $(form).find('div.cke').remove()
    $(form).find('textarea[data-type=ckeditortype]').each(function() {
        let textarea = $(this)
        let config = JSON.parse(textarea.attr('data-config'));
        CKEDITOR.replace(this.id, config)
        textarea.attr('data-processed', 1)
    })
}
