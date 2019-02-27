import { initCore } from 'src/lib/init.js'
import renderComponents from 'src/lib/renderComponents.js'
import 'vis/dist/vis.css'
import graphicalRepresentation from '@/graphicalRepresentation.vue'


initCore()
renderComponents({
    'graphical-representation': graphicalRepresentation,
})