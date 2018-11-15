import init, { initWidgets } from 'src/lib/init.js'
import { initChangeStatus } from 'src/lib/changeStatus.js'

import Vue from 'vue'
import rootComponent from '@/root/itemPage.js'

import 'src/styles/aristotle.autocomplete.css'
import 'src/styles/aristotle.wizard.less'
import 'src/styles/aristotle_search.less'

export function initItemPage() {
    init()

    $(document).ready(function() {
        $('.modal').on('loaded.bs.modal', function() {
            initChangeStatus()
            initWidgets()
        })
    })

    new Vue(rootComponent)
}
