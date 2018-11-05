<template>
  <div>
    <div class="form-group">
      <label for="name">Name</label>
      <input id="name" class="form-control"></input>
    </div>
    <div class="form-group">
      <label for="name">Description</label>
      <textarea id="name" class="form-control"></textarea>
    </div>
  </div>
</template>

<script>
export default {
    props: ['iid']
}
</script>
