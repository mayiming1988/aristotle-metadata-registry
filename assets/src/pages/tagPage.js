import renderComponents from 'src/lib/renderComponents.js'
import { initCore } from 'src/lib/init.js'

import switchEditComponent from '@/switchEdit.vue'

import 'src/styles/taggle.css'
import 'src/styles/aristotle.dashboard.less'

initCore()
renderComponents({'switch-edit': switchEditComponent})
