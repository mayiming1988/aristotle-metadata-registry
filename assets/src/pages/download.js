import initCore from 'src/lib/init.js'
import renderComponents from 'src/lib/renderComponents.js'
import downloadComponent from '@/download.vue'

initCore()
renderComponents({download: downloadComponent})
