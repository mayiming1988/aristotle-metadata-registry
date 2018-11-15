import { initCore } from '../lib/init.js'

import Vue from 'vue'
import rootComponent from '@/root/issues.js'


initCore()
new Vue(rootComponent)
