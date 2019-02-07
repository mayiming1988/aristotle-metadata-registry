<template>
    <div>
        Hello world {{ url }}
    </div>
</template>

<script>
    export default {
        props: ['url'],
        name: "graphicalRepresentation",
        mounted() {
            console.log("HEllo there!")
            $.getJSON(this.url, (data) => {
                console.log(data)
            })
        }
    }
</script>

<style scoped>

</style>