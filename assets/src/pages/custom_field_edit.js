import Vue from 'vue'
import VeeValidate from 'vee-validate'
import vvConfig from 'src/config/vee-validate.js'

import { initCore } from 'src/lib/init.js'
import customFieldEditRoot from '@/root/customFieldEdit.js'

initCore()
Vue.use(VeeValidate, vvConfig)
new Vue(customFieldEditRoot)
