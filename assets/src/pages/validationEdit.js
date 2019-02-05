import { initCore } from 'src/lib/init.js'
import 'src/styles/aristotle.dashboard.less'
import renderComponents from 'src/lib/renderComponents.js'
import yamlEditor from '@/yamlEditor.vue'

initCore()
renderComponents({
    'yaml-editor': yamlEditor
})
