<template>
    <textarea ref="te" class="ckeditor-vue" :value="initial" />
</template>

<script>
import { initCKEditorFromTextarea } from 'src/lib/ckeditor_simple_init.js'

export default {
    props: {
        value: {
            type: String,
            default: ''
        },
        jsonConfig: {
            type: String,
            default: '{}'
        }
    },
    data: () => ({
        initial: '',
        displayed: ''
    }),
    created: function() {
        this.initial = this.value
        this.config = JSON.parse(this.jsonConfig)
    },
    mounted: function() {
        this.editor = initCKEditorFromTextarea(this.$refs.te, this.config)
        this.editor.on('change', this.onEditorChange)
    },
    methods: {
        onEditorChange: function(event) {
            this.displayed = event.editor.getData()
            this.$emit('input', this.displayed)
        }
    },
    watch: {
        value: function(newval) {
            if (this.displayed !== newval) {
                this.editor.setData(newval)
            }
        }
    }
}
</script>
