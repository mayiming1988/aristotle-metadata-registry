import Vue from 'vue'

import { initCore } from 'src/lib/init.js'
import customFieldEditRoot from '@/root/customFieldEdit.js'

initCore()
new Vue(customFieldEditRoot)
