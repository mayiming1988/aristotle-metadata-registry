import axios from 'axios'
import { getCSRF } from 'src/lib/cookie.js'

export default function(method, url, data) {
    let csrf_token = getCSRF()
    let promise = axios({
        method: method,
        url: url,
        data: data,
        headers: {'X-CSRFToken': csrf_token}
    })
    return promise
}
