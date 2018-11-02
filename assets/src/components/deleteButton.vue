<template>
  <button class="btn btn-danger" @click="deleteClicked">Delete</button>
</template>

<script>
export default {
    props: ['itemName', 'itemId'],
    methods: {
        deleteClicked: function(e) {
            var item = {
                id: this.itemId,
                name: this.itemName,
                target: e.target
            }
            this.$emit('click', item)
        }
    }
}
</script>
