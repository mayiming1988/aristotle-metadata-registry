<template>
  <button class="btn" :class="buttonType" @click="deleteClicked">{{ buttonText }}</button>
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
      },
      modalText: {
        type: String,
        default: 'Are you sure you want to delete'
      }
    },
    methods: {
        deleteClicked: function(e) {
            var item = {
                modalText: this.modalText,
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
