<script>
import switchEdit from '@/switchEdit.vue'
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    extends: switchEdit,
    mixins: [apiRequest],
    methods: {
        submitInput: function() {
            let data = {}
            data[this.name] = this.value
            this.patch(this.submitUrl, data)
            .then(() => {
                this.editing = false
            })
        }
    }
}
</script>
