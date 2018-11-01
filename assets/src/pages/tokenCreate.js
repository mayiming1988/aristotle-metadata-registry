import { initCore } from '../lib/init.js'
import ClipboardJS from 'clipboard'
import { initJsonEditor } from '../lib/json_editor_init.js'

initCore()

if (ClipboardJS.isSupported()) {
  new ClipboardJS('#copybutton');
} else {
  $('#copybutton').remove()
}

initJsonEditor()
