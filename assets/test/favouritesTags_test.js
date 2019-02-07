import chai from 'chai'
import VueTestUtils from '@vue/test-utils'
import sinon from 'sinon'

import { addMessageRow, assertSingleMessage, fakePromiseMethod } from './utils.js'
import favouriteComponent from '@/favourite.vue'
import tagComponent from '@/tags/tag.vue'
import autoCompleteTagComponent from '@/tags/autocompleteTag.vue'
import tagsModal from '@/tags/tagsModal.vue'
import submitTags from '@/tags/submitTags.vue'
import allTagsRoot from '@/root/allTags.js'

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
        assert.equal(wrapper.vm.linkTitle, 'Remove from my favourites')
        wrapper.setData({favourited: false})
        assert.equal(wrapper.vm.linkTitle, 'Add to my favourites')
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
        this.user_tags = [
            {'id': 7, 'name': 'amazing'},
            {'id': 9, 'name': 'very good'},
            {'id': 10, 'name': 'sweet'}
        ]
        this.item_tags = [
            {'tag__id': 8, 'tag__name': 'ok'},
            {'tag__id': 6, 'tag__name': 'not so good'}
        ]

        wrapper = shallowMount(tagsModal, {
            propsData: {
                itemTags: JSON.stringify(this.item_tags),
                userTags: JSON.stringify(this.user_tags)
            }
        })
    })

    it('sets initial tags from json', () => {
        assert.deepEqual(wrapper.vm.user_tags, this.user_tags)
        assert.deepEqual(wrapper.vm.current_tags, ['ok', 'not so good'])
    })

    it('emits initial saved tags', () => {
        let emitted = wrapper.emitted()

        assert.equal(emitted['saved-tags'].length, 1)
        let emmitted_tags = emitted['saved-tags'][0][0]
        assert.equal(emmitted_tags[0]['name'], 'ok')
        assert.equal(emmitted_tags[0]['id'], 8)
        assert.equal(emmitted_tags[1]['name'], 'not so good')
        assert.equal(emmitted_tags[1]['id'], 6)
    })

    it('updates current tags', () => {
        let tags = ['wow', 'brilliant']
        wrapper.vm.update_tags(tags)
        assert.deepEqual(wrapper.vm.current_tags, tags)
    })

    it('updates saved tags', () => {
        let tags = [
            {'id': 11, 'name': 'wow'},
            {'id': 12, 'name': 'great'}
        ]
        wrapper.vm.update_saved_tags(tags)

        let emitted = wrapper.emitted()
        assert.equal(emitted['saved-tags'].length, 2)
        assert.equal(emitted['saved-tags'][1][0], tags)
    })

    it('updates user tags when tags saved', () => {
        let tags = [
            {'id': 8, 'name': 'ok'}, 
            {'id': 6, 'name': 'not so good'}, 
            {'id': 7, 'name': 'amazing'}, 
            {'id': 10, 'name': 'sweet'}
        ]
        let newusertags = [
            {'id': 7, 'name': 'amazing'}, 
            {'id': 9, 'name': 'very good'},
            {'id': 10, 'name': 'sweet'},
            {'id': 8, 'name': 'ok'}, 
            {'id': 6, 'name': 'not so good'}
        ]
        wrapper.vm.update_saved_tags(tags)
        assert.deepEqual(wrapper.vm.user_tags, newusertags)
    })
})

describe('submitTags', function() {

    beforeEach(function() {
        this.wrapper = shallowMount(submitTags, {
            propsData: {
                submitUrl: '/submittags',
                tags: ['wow', 'amazing', 'good']
            }
        })
    })

    it('calculates tags list', function() {
        assert.deepEqual(
            this.wrapper.vm.tagsList,
            [{name: 'wow'}, {name: 'amazing'}, {name: 'good'}]
        )
    })

    it('submits tags and displays message', function() {
        let fakepost = fakePromiseMethod(this.wrapper, 'put')
        this.wrapper.vm.submit_tags()
        assert.isTrue(fakepost.calledOnce)
        assert.isTrue(
            fakepost.firstCall.calledWithExactly(
                '/submittags',
                {tags: [{name: 'wow'}, {name: 'amazing'}, {name: 'good'}]}
            )
        )
    })

    it('emits tags and displays message', function() {
        addMessageRow(document.body)

        let response = {'tags': [{'id': 7, 'name': 'woah'}]}
        fakePromiseMethod(this.wrapper, 'put', {data: response})

        this.wrapper.vm.submit_tags()
        
        return this.wrapper.vm.$nextTick().then(() => {
            // Check message and emit
            assertSingleMessage('Tags Saved')
            let emitted = this.wrapper.emitted()
            assert.equal(emitted['tags-saved'].length, 1)
            assert.deepEqual(emitted['tags-saved'][0][0], response['tags'])

            // Cleanup dom
            document.getElementById('messages-row').remove()
        })
    })
})


describe('allTagsRoot', function() {

    beforeEach(function() {
        let initData = allTagsRoot.data
        this.wrapper = shallowMount(allTagsRoot, {
            data: () => (initData)
        })
    })

    it('sets state on delete clicked', function() {
        this.wrapper.vm.deleteClicked({name: 'MyTag', url: 'tags/mytag'})
        assert.equal(this.wrapper.vm.modal_text, 'Are you sure you want to delete MyTag')
        assert.isTrue(this.wrapper.vm.modal_visible)
        assert.deepEqual(this.wrapper.vm.tag_item, {name: 'MyTag', url: 'tags/mytag'})
    })
    
    it('hides modal on delete cancelled', function() {
        this.wrapper.setData({modal_visible: true})
        this.wrapper.vm.deleteCancelled()
        assert.isFalse(this.wrapper.vm.modal_visible)
    })

    it('makes request on delete confirmed', function() {
        let fake = fakePromiseMethod(this.wrapper, 'delete')
        this.wrapper.setData({tag_item: {url: 'tags/5'}})
        this.wrapper.vm.deleteConfirmed()
        assert.isTrue(fake.calledWithExactly('tags/5'))
    })
})
