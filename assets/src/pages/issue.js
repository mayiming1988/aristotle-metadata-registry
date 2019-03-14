// Individual issue page
import { initCore } from 'src/lib/init.js'

import Vue from 'vue'
import rootComponent from '@/root/issues.js'


initCore()
new Vue(rootComponent)
