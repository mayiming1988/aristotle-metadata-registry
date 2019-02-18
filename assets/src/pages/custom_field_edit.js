import { initCore } from 'src/lib/init.js'
import renderComponents from 'src/lib/renderComponents.js'
import apiFormSet from '@/djforms/apiFormSet.vue'

import 'src/styles/aristotle.dashboard.less'

initCore()
renderComponents({'formset': apiFormSet})
