<template>
    <li class="dropdown">
        <a id="header_menu_button_notifications"
           class="dropdown-toggle" 
           data-toggle="dropdown" 
           title="">
            <span :class="notifyClass" title=""></span>
        </a>
        <ul class="dropdown-menu">
        </ul>
    </li>
</template>

<script>
export default {
    props: ['unreadListUrl', 'markAllReadUrl', 'initialCount'],
    data: () => ({
        loading: false,
        count: 0
    }),
    created: function() {
        this.count = this.initialCount
    },
    computed: {
        notifyClass: function() {
            if (this.count > 0) {
                return 'notify'
            } else {
                return 'no-notify'
            }
        }
    }
}
</script>
