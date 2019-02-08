<script>
import rulesEditor from '@/rules/rulesEditor.vue'

export default {
    extends: rulesEditor,
    props: {
        update_url_template: String,
        method: {
            type: String,
            default: 'put',
        },
        ra_id: String
    },
    created: function() {
        this.submit_url = this.api_url
        this.submit_method = this.method
    },
    methods: {
        submitData: function(data) {
            data['registration_authority'] = parseInt(this.ra_id) // Set ra id
            let func = this[this.submit_method] // Gets this.put this.post etc
            console.log(this.submit_url)
            console.log(this.submit_method)
            func(this.submit_url, data).then((response) => {
                this.updated = true
                // If we just created an item
                if (response.status == 201) { 
                    console.log('got a 201')
                    // Switch to update url
                    this.submit_url = this.update_url_template.replace('{pk}', response.data.id)
                    this.submit_method = 'put'
                }
            })
        }
    }
}
</script>
