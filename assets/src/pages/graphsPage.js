import { initCore } from 'src/lib/init.js'

import Vue from 'vue'
import rootComponent from '@/root/graphsPage.js'


initCore()
new Vue(rootComponent)