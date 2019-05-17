<template>
    <div class="selectTagger">
        <select class="left-select" @input="tagSelected">
            <option value="">{{ emptyOption }}</option>
            <option v-for="option in currentOptions" :key="option" :value="option">{{ option }}</option>
        </select>
        <ul class="taggle_list">
            <li v-for="tag in value" class="taggle" :key="tag" :value="tag">
                <span clas="taggle_text">{{ tag }}</span>
                <button class="close" @click="removeTag(tag)">×</button>
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
        Stores options the user is allowed to select from
        this avoids letting them add duplicates
        */
        currentOptions: new Set()
    }),
    props: {
        // Currently selected tags
        value: {
            type: Array,
            required: true
        },
        // List of all tags (used as initial options)
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
        this.currentOptions = new Set(this.options)
    },
    methods: {
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

.taggle_list {
    width: auto;
}
</style>
