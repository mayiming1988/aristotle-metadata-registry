<template>
    <div :id="tagId" class="yaml-editor" />
</template>

<script>
// Import codemirror
import CodeMirror from 'codemirror'
// Import yaml mode
import 'codemirror/mode/yaml/yaml.js'

export default {
    props: {
        id: {
            type: Number,
            default: 1
        },
        value: {
            type: String,
            default: ''
        }
    },
    mounted: function() {
        this.codeMirror = CodeMirror(
            document.querySelector('#' + this.tagId + '.yaml-editor'),
            {
                mode: 'yaml',
                lineNumbers: true,
                value: this.value
            }
        )
        this.codeMirror.addKeyMap({
            "Tab": function (cm) {
                cm.execCommand("insertSoftTab");
            },
        });
        this.codeMirror.getDoc().on('change', this.editorChange)
    },
    computed: {
        tagId: function() {
            return 'yaml-editor-' + this.id
        }
    },
    methods: {
        editorChange: function(doc) {
            this.$emit('input', doc.getValue())
        }
    }
}
</script>

<style>
@import '~codemirror/lib/codemirror.css';

.yaml-editor {
    border: grey solid 1px;
}
</style>
