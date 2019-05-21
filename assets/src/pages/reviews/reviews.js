import { initCore } from 'src/lib/init.js'

import Vue from 'vue'
import rootComponent from '@/reviews/root.js'


initCore()
new Vue(rootComponent)
