<template>
<div>
    <div v-for="item in items">
        <div v:if="item.data">
        <comment v-if="item.type == 'comment'"
            :key="item.data.id"
            :pic="item.data.pic"
            :name="item.data.name"
            :created="item.data.created"
            :body="item.data.body">
        </comment>
        <status-change-timeline v-if="item.type == 'status_change'"
            :name="item.data.name"
            :status="item.data.status_code"
            >
        </status-change-timeline>
        </div>
  </div>
  </div>
</template>

<script>
import comment from '@/comment.vue'
import statusChangeTimeline from '@/reviews/statusChange.vue'

export default {
    props: ['items'],
    components: {
        comment,
        statusChangeTimeline,
    },
}
</script>

<style>
</style>
