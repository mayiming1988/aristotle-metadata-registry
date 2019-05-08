<template>
    <textarea ref="te" class="ckeditor-vue" :value="initial" />
</template>

<script>
import { initCKEditorFromTextarea } from 'src/lib/ckeditor_simple_init.js'

export default {
    props: {
        value: {
            type: String,
            default: 'Spicy'
        },
        jsonConfig: {
            type: String,
            default: '{}'
        }
    },
    data: () => ({
        initial: '',
    }),
    created: function() {
        this.initial = this.value
        this.config = JSON.parse(this.jsonConfig)
    },
    mounted: function() {
        initCKEditorFromTextarea(this.$refs.te, this.config)
    }
}
</script>
