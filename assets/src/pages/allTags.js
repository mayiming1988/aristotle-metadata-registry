import { initCore } from '../lib/init.js'

import rootComponent from '@/root/allTags.js'
import Vue from 'vue'

import '../styles/aristotle.dashboard.less'

initCore()
new Vue(rootComponent)
