import chai from 'chai'
const assert = chai.assert

import { flatten, unCamel } from 'src/lib/utils.js'


describe('flatten', function() {

    it('Flattens when attr defined', function() {
        let array = [{a: 'Hell', b: 'Yeah'}, {a: 'Heck', b: 'Yea'}]
        let result = flatten(array, 'a')
        assert.deepEqual(result, ['Hell', 'Heck'])
    })

    it('Flattens when attr undefined', function() {
        let array = [{a: 'Hell', b: 'Yeah'}, {b: 'Yea'}]
        let result = flatten(array, 'a')
        assert.deepEqual(result, ['Hell', undefined])
    })
})

describe('uncamel', function() {

    it('Un camel cases single', function() {
        let camel = 'camelCase'
        let result = unCamel(camel)
        assert.equal(result, 'camel Case')
    })

    it('Un camel cases double', function() {
        let camel = 'moreCamelCase'
        let result = unCamel(camel)
        assert.equal(result, 'more Camel Case')
    })
})
