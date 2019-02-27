import init, { initWidgets } from 'src/lib/init.js'
import { initMoveable } from './moveable.js'
import { initChangeStatus } from 'src/lib/changeStatus.js'
import { initConceptLinks } from 'src/lib/concept_links.js'

import Vue from 'vue'
import rootComponent from '@/root/itemPage.js'

import 'src/styles/aristotle.wizard.less'
import 'src/styles/aristotle_search.less'
import 'src/styles/conceptlink.css'

export function initItemPage() {
    init()
    initMoveable()
    initConceptLinks()

    $(document).ready(function() {
        $('.modal').on('loaded.bs.modal', function() {
            initChangeStatus()
            initWidgets()
            initMoveable()
        })
    })

    new Vue(rootComponent)
}
