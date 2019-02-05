<template>
    <div class="yaml-editor">
        <textarea>{{ value }}</textarea>
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
        this.codeMirror = CodeMirror.fromTextArea(
            document.querySelector('.yaml-editor>textarea'),
            {
                mode: 'yaml',
                lineNumbers: true,
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
