import init from '../lib/init.js'
import ClipboardJS from 'clipboard'
import { initJsonEditor } from '../lib/json_editor_init.js'

init(false)

if (ClipboardJS.isSupported()) {
  new ClipboardJS('#copybutton');
} else {
  $('#copybutton').remove()
}

initJsonEditor()
