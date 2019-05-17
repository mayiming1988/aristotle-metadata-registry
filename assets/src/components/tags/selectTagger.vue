<template>
    <div class="selectTagger">
        <select class="left-select" @input="tagSelected">
            <option value="">{{ emptyOption }}</option>
            <option v-for="val in currentOptions" :key="val" :value="val">{{ getText(val) }}</option>
        </select>
        <ul class="taggle_list">
            <li v-for="val in value" class="taggle" :key="val">
                <span clas="taggle_text">{{ getText(val) }}</span>
                <button class="close" @click="removeTag(val)">×</button>
            </li>
        </ul>
    </div>
</template>

<script>
/*
Simple tagging from a predefined list with a select box
Has v-model support
*/
export default {
    data: () => ({
        /* 
        Stores options objects the user is allowed to select from
        this avoids letting them add duplicates
        */
        currentOptions: new Set(),
        valueMap: new Map()
    }),
    props: {
        // Currently selected tags
        value: {
            type: Array,
            required: true
        },
        // List of all tags as options objects (used as initial options)
        options: {
            type: Array,
            required: true
        },
        // Empty option text
        emptyOption: {
            type: String,
            default: '------'
        }
    },
    created: function() {
        // Build valueMap and current options
        for (let option of this.options) {
            this.valueMap.set(option.value, option.text)
            this.currentOptions.add(option.value)
        }
        // Remove initial tags from current options
        for (let tag of this.value) {
            this.currentOptions.delete(tag)
        }
    },
    methods: {
        getText: function(value) {
            let name = this.valueMap.get(value)
            if (name === undefined) {
                name = ''
            }
            return name
        },
        tagSelected: function(event) {
            let option = event.target.options[event.target.selectedIndex]
            let selection = option.value
            if (selection.length > 0) {
                // Emit new labels
                let newLabels = this.value
                newLabels.push(selection)
                this.$emit('input', newLabels)
                // Remove option
                this.currentOptions.delete(selection)
            }
        },
        removeTag: function(tagToDelete) {
            // Filter out tag we are deleting
            let newLabels = this.value.filter(tag => tag !== tagToDelete)
            // Add back to options
            this.currentOptions.add(tagToDelete)
            // Emit new value
            this.$emit('input', newLabels)
        }
    }
}
</script>

<style>
@import '../../styles/taggle.css';

select.left-select {
    float: left;
}
</style>
