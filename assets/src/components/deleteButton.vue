<template>
  <button class="btn btn-danger" @click="deleteClicked">Delete</button>
</template>

<script>
export default {
    props: ['itemName', 'itemId', 'url'],
    methods: {
        deleteClicked: function(e) {
            var item = {
                id: this.itemId,
                name: this.itemName,
                url: this.url,
                target: e.target
            }
            this.$emit('click', item)
        }
    }
}
</script>
