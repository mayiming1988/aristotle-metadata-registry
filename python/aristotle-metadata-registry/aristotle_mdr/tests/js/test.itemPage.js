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
    const wrapper = mount(favouriteComponent)
    wrapper.setData({favourited: true})
    assert.equal(wrapper.vm.linkTitle, 'Add to my favourites')
    wrapper.setData({favourited: false})
    assert.equal(wrapper.vm.linkTitle, 'Remove from my favourites')
  })

  it('sets icon class correctly', function() {
    const wrapper = mount(favouriteComponent)
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
    assert.equal(elements[2].className, 'taggle  taggle_newtag')
    assert.equal(elements[1].className, 'taggle')
    assert.equal(elements[0].className, 'taggle')
  })

  it('emits tag updates', function() {
    wrapper.vm.tag_editor.add('wow')
    assert.exists(wrapper.emitted('tag-update'))
    assert.deepEqual(wrapper.emitted('tag-update')[0][0], ['tag1', 'tag2', 'wow'])

    wrapper.vm.tag_editor.remove('wow')
    console.log(wrapper.emitted('tag-update'))
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
