import chai from 'chai'
import VueTestUtils from '@vue/test-utils'
import sinon from 'sinon'

import { addMessageRow, assertSingleMessage } from './utils.js'
import favouriteComponent from '@/favourite.vue'
import tagComponent from '@/tags/tag.vue'
import autoCompleteTagComponent from '@/tags/autocompleteTag.vue'
import tagsModal from '@/tags/tagsModal.vue'
import submitTags from '@/tags/submitTags.vue'

var assert = chai.assert
var mount = VueTestUtils.mount
var shallowMount = VueTestUtils.shallowMount

describe('favouriteComponent', function() {
    it('has a created hook', function() {
        assert.typeOf(favouriteComponent.created, 'function')
    })

    it('sets initial state correctly', function() {
        var wrapper = mount(favouriteComponent, {
            propsData: {initial: 'True'}
        })
        assert.equal(wrapper.vm.favourited, true)

        wrapper = mount(favouriteComponent, {
            propsData: {initial: 'False'}
        })
        assert.equal(wrapper.vm.favourited, false)
    })

    it('sets title correctly', function() {
        var wrapper = mount(favouriteComponent)
        wrapper.setData({favourited: true})
        assert.equal(wrapper.vm.linkTitle, 'Add to my favourites')
        wrapper.setData({favourited: false})
        assert.equal(wrapper.vm.linkTitle, 'Remove from my favourites')
    })

    it('sets icon class correctly', function() {
        var wrapper = mount(favouriteComponent)
        wrapper.setData({favourited: true})
        assert.equal(wrapper.vm.iconClass, 'fa fa-bookmark')
        wrapper.setData({favourited: false})
        assert.equal(wrapper.vm.iconClass, 'fa fa-bookmark-o')
    })
})

describe('tagComponent', function() {

    var wrapper

    beforeEach(function() {
        wrapper = mount(tagComponent, {
            attachToDocument: true,
            propsData: {tags: ['tag1', 'tag2']}
        })
    })

    afterEach(function() {
        $('#taggle-editor').remove()
    })

    it('displays tags', function() {
        assert.deepEqual(wrapper.vm.tag_editor.getTagValues(), ['tag1', 'tag2'])
    })

    it('updates tags from prop', function() {
        wrapper.setProps({tags: ['tag1', 'tag2', 'tag3']})
        assert.deepEqual(wrapper.vm.tag_editor.getTagValues(), ['tag1', 'tag2', 'tag3'])
    })

    it('updates class with newtags', function() {
        wrapper.setProps({tags: ['tag1', 'tag2', 'tag3'], newtags: ['tag3']})
        var elements = wrapper.vm.tag_editor.getTagElements()
        assert.equal(elements[2].className, 'taggle taggle_newtag')
        assert.equal(elements[1].className, 'taggle')
        assert.equal(elements[0].className, 'taggle')
    })

    it('emits tag updates', function() {
        wrapper.vm.tag_editor.add('wow')
        assert.exists(wrapper.emitted('tag-update'))
        assert.deepEqual(wrapper.emitted('tag-update')[0][0], ['tag1', 'tag2', 'wow'])

        wrapper.vm.tag_editor.remove('wow')
        assert.deepEqual(wrapper.emitted('tag-update')[1][0], ['tag1', 'tag2'])
    })
})

describe('autoCompleteTagComponent', function() {

    var wrapper

    beforeEach(function() {
        wrapper = shallowMount(autoCompleteTagComponent, {
            propsData: {
                current_tags: ['tag1', 'tag2'],
                user_tags: ['tag1', 'someothertag', 'morenewtags']
            }
        })
    })

    it('computes new tags', function() {
        assert.deepEqual(wrapper.vm.newTags, ['tag2'])
    })

    it('computes suggestions', function() {
        assert.deepEqual(wrapper.vm.getSuggestions(), ['someothertag', 'morenewtags'])
    })

    it('adds suggetsions', function() {
        wrapper.vm.makeSuggestion('someothertag')
        assert.deepEqual(wrapper.vm.current_tags, ['tag1', 'tag2', 'someothertag'])
    })

})

describe('tagsModal', function() {

    var wrapper

    beforeEach(() => {
        let user_tags = ['amazing', 'very good', 'sweet']
        let item_tags = ['ok', 'not so good']

        wrapper = shallowMount(tagsModal, {
            propsData: {
                itemTags: JSON.stringify(item_tags),
                userTags: JSON.stringify(user_tags)
            }
        })
    })

    it('sets initial tags from json', () => {
        assert.deepEqual(wrapper.vm.user_tags, ['amazing', 'very good', 'sweet'])
        assert.deepEqual(wrapper.vm.current_tags, ['ok', 'not so good'])
        assert.deepEqual(wrapper.vm.saved_tags, ['ok', 'not so good'])
    })

    it('emits initial saved tags', () => {
        let emitted = wrapper.emitted()

        assert.equal(emitted['saved-tags'].length, 1)
        assert.deepEqual(emitted['saved-tags'][0][0], ['ok', 'not so good'])
    })

    it('updates current tags', () => {
        let tags = ['wow', 'brilliant']
        wrapper.vm.update_tags(tags)
        assert.deepEqual(wrapper.vm.current_tags, tags)
    })

    it('updates saved tags', () => {
        let tags = ['wow', 'great']
        wrapper.vm.update_saved_tags(tags)
        assert.deepEqual(wrapper.vm.saved_tags, tags)

        let emitted = wrapper.emitted()
        assert.equal(emitted['saved-tags'].length, 2)
        assert.equal(emitted['saved-tags'][1][0], tags)
    })

    it('updates user tags when tags saved', () => {
        let tags = ['ok', 'not so good', 'amazing', 'sweet']
        let newusertags = ['amazing', 'very good', 'sweet', 'ok', 'not so good']
        wrapper.vm.update_saved_tags(tags)
        assert.deepEqual(wrapper.vm.saved_tags, tags)
        assert.deepEqual(wrapper.vm.user_tags, newusertags)
    })
})

describe('submitTags', function() {

    var wrapper

    beforeEach(function() {
        wrapper = shallowMount(submitTags, {
            propsData: {
                submitUrl: '/submittags',
                tags: ['wow', 'amazing', 'good']
            }
        })

        this.server = sinon.createFakeServer()
    })

    afterEach(function() {
        this.server.restore()
    })

    it('submits tags and displays message', function() {
        addMessageRow(document.body)

        let response = {'success': true, 'message': 'Tags updated'}
        this.server.respondWith([
            200,
            {'Content-Type': 'application/json'},
            JSON.stringify(response)
        ])

        wrapper.vm.submit_tags()
        this.server.respond()

        assert.equal(this.server.requests.length, 1)
        let request = this.server.requests[0]
        assert.equal(request.url, '/submittags')
        assert.equal(request.method, 'POST')

        // Check submitted tags
        let params = new URLSearchParams(request.requestBody)
        let tags = JSON.parse(params.get('tags'))
        assert.deepEqual(tags, ['wow', 'amazing', 'good'])

        // Check message and emit
        assertSingleMessage('Tags updated')
        let emitted = wrapper.emitted()
        assert.equal(emitted['tags-saved'].length, 1)
        assert.deepEqual(emitted['tags-saved'][0][0], ['wow', 'amazing', 'good'])

        // Cleanup dom
        document.getElementById('messages-row').remove()
    })
})
