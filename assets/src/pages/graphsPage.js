import { initCore } from 'src/lib/init.js'
import renderComponents from 'src/lib/renderComponents.js'
import graphsPage from '@/graphs/graphsPage.vue'


initCore()
renderComponents({
    'graphs-page': graphsPage
})
