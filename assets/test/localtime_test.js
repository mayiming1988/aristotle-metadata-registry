import chai from 'chai'
const assert = chai.assert

import { initTime } from 'src/lib/localtime.js'

describe('initTime', function() {

    beforeEach(function() {
        let timetag = document.createElement('time')
        document.body.appendChild(timetag)
        this.timetag = timetag
    })

    afterEach(function() {
        document.body.removeChild(this.timetag)
    })

    it('Converts datetime to default format', function() {
        this.timetag.setAttribute('datetime', '2017-01-01')
        assert.equal(this.timetag.textContent, '')
        initTime()
        assert.equal(this.timetag.textContent, '1st January 2017')
    })
})
