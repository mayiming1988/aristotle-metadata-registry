<script>
import switchEdit from '../components/switchEdit.vue'
import apiRequest from '../mixins/apiRequest.js'

export default {
    extends: switchEdit,
    mixins: [apiRequest],
    methods: {
        submitInput: function() {
            let data = {}
            data[this.name] = this.value
            this.patch(this.submitUrl, data)
            .then((response) => {
                if (response.status == 200) {
                    this.editing = false
                }
            })
        }
    }
}
</script>
