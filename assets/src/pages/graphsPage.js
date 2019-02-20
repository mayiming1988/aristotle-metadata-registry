import { initCore } from 'src/lib/init.js'
import renderComponents from 'src/lib/renderComponents.js'
import 'vis/dist/vis.css'
import supersedesGraphicalRepresentation from '@/supersedesGraphicalRepresentation.vue'
import generalGraphicalRepresentation from '@/generalGraphicalRepresentation.vue'


initCore()
renderComponents({
    'supersedes-graphical-representation': supersedesGraphicalRepresentation,
    'general-graphical-representation': generalGraphicalRepresentation
})