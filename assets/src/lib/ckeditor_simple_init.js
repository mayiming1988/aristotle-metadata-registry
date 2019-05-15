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
    let editor = null
    let processed = textarea.getAttribute('data-processed')
    if (processed == 0 || processed == null) {
        // If config not provided use data-config
        if (config === undefined) {
            config = JSON.parse(textarea.getAttribute('data-config'));
        }
        editor = CKEDITOR.replace(textarea, config)
        textarea.setAttribute('data-processed', 1)
    }
    return editor
}

// ReInitialize ckeditor instances
export function reinitCKEditors(form) {
    for (let div of form.querySelectorAll('div.cke')) {
        div.parentNode.removeChild(div)        
    }
    initCKEditor()
}
