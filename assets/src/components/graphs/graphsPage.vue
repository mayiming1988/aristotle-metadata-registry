<template>
    <sideMenu :items="menuItems" />
</template>

<script>
import sideMenu from '@/sideMenu.vue'

export default {
    components: {
        sideMenu
    },
    data: () => ({
        menuItems: ['General', 'Supersedes', 'Links']
    })
}
</script>
