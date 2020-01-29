import reviewConfirmRoot from "@/root/reviewConfirmRoot.js";
import {addHeaderMessage, initMessages} from 'src/lib/messages.js'
initMessages();

export default {
    extends: reviewConfirmRoot,
    methods: {
        actionConfirmed: function() {
            let data = {"concept_id": this.item.id};
            this.put(this.item['url'], data)
                .then(() => {
                    this.modal_visible = false;
                    addHeaderMessage("Promoting item to main item review was successful");
                    this.item.target.disabled = "true";
                    this.item.target.innerText = "Promoted";
                })
        },
    }
}