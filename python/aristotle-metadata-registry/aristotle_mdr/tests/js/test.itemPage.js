var assert = chai.assert
var mount = VueTestUtils.mount

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
