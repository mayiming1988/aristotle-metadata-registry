import chai from 'chai'
const assert = chai.assert
import VueTestUtils from '@vue/test-utils'

import yamlEditor from '@/yamlEditor.vue'


describe('yamlEditor', function() {

    function mountEditor(initial_props={}) {
        return VueTestUtils.mount(yamlEditor, {attachToDocument: true, propsData: initial_props})
    }

    it('instanciated codemirror', function() {
        let wrapper = mountEditor()
        // Check that codemirror was mounted
        let cm = wrapper.element.querySelector('.CodeMirror')
        assert.isNotNull(cm)
        wrapper.destroy()
    })

    it('emits input on document change', function() {
        let wrapper = mountEditor()
        // update document
        wrapper.vm.codeMirror.getDoc().setValue('some content')
        return wrapper.vm.$nextTick().then(() => {
            // check events
            let input_events = wrapper.emitted().input
            assert.equal(input_events.length, 1)
            assert.equal(input_events[0][0], 'some content')
            wrapper.destroy()
        })
    })

    it('sets document to initial value', function() {
        let wrapper = mountEditor({value: 'initial content'})
        let value = wrapper.vm.codeMirror.getDoc().getValue()
        assert.equal(value, 'initial content')
        wrapper.destroy()
    })

    it('computes tag id', function() {
        let wrapper = VueTestUtils.shallowMount(
            yamlEditor,
            {propsData: {id: 5}}
        )
        assert.equal(wrapper.vm.tagId, 'yaml-editor-5')
    })

})
