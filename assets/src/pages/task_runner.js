import { initCore } from 'src/lib/init.js'

import Vue from 'vue'
import rootComponent from '@/tasks/tasklist.js'


initCore()
new Vue(rootComponent)
