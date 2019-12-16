import reviewConfirmRoot from "@/root/reviewConfirmRoot.js";

export default {
    extends: reviewConfirmRoot,
    methods: {
        actionConfirmed: function () {
            let data = {"concept_id": this.item.id}
            this.put(this.item['url'], data)
                .then(() => {
                    $(this.item.target).closest('tr').remove()
                    this.modal_visible = false
                })
        },

    }
}


