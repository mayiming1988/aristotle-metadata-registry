<template>
  <div class="form-group">
    <label :for="name">{{ capitalize(name) }}</label>
    <slot :id="name"></slot>
  </div>
</template>

<script>
export default {
    props: ['name'],
    methods: {
        capitalize: (name) => {
            let first = name.charAt(0)
            return first.toUpperCase() + name.slice(1)
        }
    }
}
</script>
