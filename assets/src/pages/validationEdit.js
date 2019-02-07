import { initCore } from 'src/lib/init.js'
import 'src/styles/aristotle.dashboard.less'
import renderComponents from 'src/lib/renderComponents.js'
import registryRulesEdit from '@/rules/registryRulesEdit.vue'

initCore()
renderComponents({
    'registry-edit-form': registryRulesEdit
})
