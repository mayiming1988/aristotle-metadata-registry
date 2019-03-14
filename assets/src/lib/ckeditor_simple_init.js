/* globals CKEDITOR */
import 'ckeditor/ckeditor.js'
import { addPlugins, addPluginConfig } from 'src/lib/ckeditor_plugins.js'
addPlugins(CKEDITOR)

export function initCKEditor() {
    $('textarea[data-type=ckeditortype]').each(function() {
        var textarea = $(this)
        var processed = textarea.attr('data-processed')
        if (processed == 0) {
            var config = JSON.parse(textarea.attr('data-config'));
            addPluginConfig(config)
            CKEDITOR.replace(this.id, config)
            textarea.attr('data-processed', 1)
        }
    })
}

export function reinitCKEditors(form) {
    $(form).find('div.cke').remove()
    $(form).find('textarea[data-type=ckeditortype]').each(function() {
        var textarea = $(this)
        var config = JSON.parse(textarea.attr('data-config'));
        CKEDITOR.replace(this.id, config)
        textarea.attr('data-processed', 1)
    })
}
