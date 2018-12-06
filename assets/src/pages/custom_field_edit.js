import Vue from 'vue'

import { initCore } from 'src/lib/init.js'
import customFieldEditRoot from '@/root/customFieldEdit.js'

import 'src/styles/aristotle.dashboard.less'

initCore()
new Vue(customFieldEditRoot)
