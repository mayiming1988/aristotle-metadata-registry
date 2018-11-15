import { initCore } from '../lib/init.js'

import Vue from 'vue'
import rootComponent from '../components/root/issue.js'


initCore()
new Vue(rootComponent)
