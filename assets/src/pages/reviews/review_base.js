import { initCore } from 'src/lib/init.js'

import openClose from '@/reviews/openClose.vue'
import renderComponents from 'src/lib/renderComponents.js'

import 'src/styles/taggle.css'

renderComponents({
    'open-close-approved': openClose
})

initCore()
