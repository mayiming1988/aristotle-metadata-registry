<template>
  <a class="btn btn-default favourite" :title="linkTitle" @click="submitFavourite">
    <i :class="iconClass"></i>
  </a>
</template>

<script>
import { addHeaderMessage } from 'src/lib/messages.js'

export default {
    props: ['initial', 'submitUrl'],
    data: function() {
        return {
            onIcon: 'fa fa-bookmark',
            favourited: false
        }
    },
    created: function() {
        if (this.initial == 'True') {
            this.favourited = true
        } else {
            this.favourited = false
        }
    },
    computed: {
        linkTitle: function() {
            if (this.favourited) {
                return 'Remove from my favourites '
            } else {
                return 'Add to my favourites'
            }
        },
        iconClass: function() {
            if (this.favourited) {
                return this.onIcon
            } else {
                return this.onIcon + '-o'
            }
        }
    },
    methods: {
        submitFavourite: function(e) {
            var component = this
            $.get(
                this.submitUrl,
                function(data) {
                    component.favourited = data.favourited
                    addHeaderMessage(data.message)
                }
            )
        }
    }
}
</script>
