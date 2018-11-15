import { initCore } from '../lib/init.js'

import Vue from 'vue'
import rootComponent from '@/root/tagPage.js'

import 'src/styles/taggle.css'
import 'src/styles/aristotle.dashboard.less'

initCore()
new Vue(rootComponent)
