<template>
    <div class="yaml-editor">
    </div>
</template>

<script>
import CodeMirror from 'codemirror'
import 'codemirror/mode/yaml/yaml.js'

export default {
    props: {
        value: {
            type: String,
            default: ''
        }
    },
    mounted: function() {
        this.codeMirror = CodeMirror(
            document.querySelector('.yaml-editor'),
            {
                mode: 'yaml',
                lineNumbers: true,
                value: this.value
            }
        )
        this.codeMirror.getDoc().on('change', this.editorChange)
    },
    methods: {
        editorChange: function(doc, changeObj) {
            this.$emit('input', doc.getValue())
        }
    }
}
</script>

<style>
@import '~codemirror/lib/codemirror.css';
</style>
