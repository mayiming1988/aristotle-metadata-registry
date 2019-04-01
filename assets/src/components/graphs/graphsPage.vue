<template>
    <div class="row">
        <div class="col-md-2">
            <sideMenu :items="menuItems" v-model="selected" />
        </div>
        <div class="col-md-10">
            <div v-if="selected == 0">
                <h2>General relationships</h2>
                <graphical-representation
                    :id="0"
                    :url="generalUrl"
                    type-of-graph="general"
                    direction="UD"
                    level-separation="100"
                    sort-method="hubsize"
                />
            </div>
            <div v-if="selected == 1">
                <h2>Superseding relationships</h2>
                <graphical-representation
                    :id="1"
                    :url="supersedesUrl"
                    type-of-graph="supersedes"
                    direction="LR"
                    level-separation="400"
                    sort-method="directed"
                    hierarchical
                />
            </div>
        </div>
    </div>
</template>

<script>
import sideMenu from '@/sideMenu.vue'
import graphicalRepresentation from '@/graphicalRepresentation.vue'

export default {
    props: {
        supersedesUrl: {
            type: String,
            required: true
        },
        generalUrl: {
            type: String,
            required: true
        },
        linksUrl: {
            type: String,
            required: true
        }
    },
    components: {
        sideMenu,
        graphicalRepresentation
    },
    data: () => ({
        menuItems: ['General', 'Supersedes', 'Links'],
        selected: 0
    })
}
</script>
