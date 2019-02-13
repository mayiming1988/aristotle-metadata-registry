import { initCore } from 'src/lib/init.js'

import Vue from 'vue'
import rootComponent from '@/root/graphsPage.js'
import 'vis/dist/vis.css'


initCore()
new Vue(rootComponent)