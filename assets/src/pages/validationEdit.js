import { initCore } from 'src/lib/init.js'
import 'src/styles/aristotle.dashboard.less'
import renderComponents from 'src/lib/renderComponents.js'
import editForm from '@/rules/editForm.vue'

initCore()
renderComponents({
    'edit-form': editForm
})
