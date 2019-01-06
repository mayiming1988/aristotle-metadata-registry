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
        initTime()
        assert.equal(this.timetag.textContent, '1st January 2017')
    })

    it('Converts datetime to custom format', function() {
        this.timetag.setAttribute('datetime', '2017-01-01')
        this.timetag.setAttribute('data-format', 'DD MM YYYY')
        initTime()
        assert.equal(this.timetag.textContent, '01 01 2017')
    })

    it('Converts datetime to from time', function() {
        this.timetag.setAttribute('datetime', '2001-01-01')
        this.timetag.setAttribute('data-time-from', 'true')
        initTime()
        assert.isTrue(this.timetag.textContent.endsWith('years ago'))
    })
})
