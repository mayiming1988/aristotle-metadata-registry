/* Generates a basic root components and renders it 
 * To reduce boilerplate */
import Vue from 'vue'

export default function(components, el='#vue-container') {
    let root = {
        el: el,
        components: components
    }
    new Vue(root)
}
