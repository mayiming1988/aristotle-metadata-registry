<template>
    <simpleList :ulClass="ulClass" :liClass="liClass" :data="data">
        <template slot-scope="slProps">
            <a :href="getUrl(slProps.item.id)">{{ slProps.item.name }}</a>
        </template>
    </simpleList>
</template>
    
<script>
import simpleList from '@/simpleList.vue'

export default {
    props: ['ulClass', 'liClass', 'data', 'linkTemplate'],
    components: {
        simpleList
    },
    data: () => ({
        idname: '{tagid}'
    }),
    methods: {
        getUrl: function(id) {
            return this.linkTemplate.replace(this.idname, id)
        }
    }
}
</script>
