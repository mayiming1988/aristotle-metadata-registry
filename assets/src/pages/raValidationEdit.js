import { initCore } from 'src/lib/init.js'
import renderComponents from 'src/lib/renderComponents.js'
import RARulesEditor from '@/rules/RARulesEditor.vue'

initCore()
renderComponents({
    'rules-editor': RARulesEditor
})
