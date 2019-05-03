<template>
  <button class="btn" :class="buttonType" @click="deleteClicked">Delete</button>
</template>

<script>
export default {
    props: {
      itemName: String,
      itemId: String,
      url: String,
      buttonType: {
        type: String,
        default: 'btn-danger',
      },
      buttonText: {
        type: String,
        default: 'Delete'
      }
    },
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
