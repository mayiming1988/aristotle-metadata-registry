import { initCore } from 'src/lib/init.js'

import rootComponent from '@/root/reviewItemPage.js'
import Vue from 'vue'

import 'src/styles/aristotle.dashboard.less'

initCore()
new Vue(rootComponent)
