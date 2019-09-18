<template>
    <div class="graphs-content row">
        <div class="col-md-2">
            <side-menu :items="menuItems" v-model="selected" />
        </div>
        <div class="col-md-10">
            <div v-if="selected == 0">
                <h2>General relationships</h2>
                <graph
                    :id="selected"
                    :url="generalUrl"
                    type-of-graph="general"
                    direction="UD"
                    level-separation="100"
                    sort-method="hubsize"
                    show-type
                />
            </div>
            <div v-if="selected == 1">
                <h2>Superseding relationships</h2>
                <graph
                    :id="selected"
                    :url="supersedesUrl"
                    type-of-graph="supersedes"
                    direction="LR"
                    level-separation="400"
                    sort-method="directed"
                    hierarchical
                />
            </div>
            <div v-if="selected == 2">
                <h2>Links relationships</h2>
                <graph
                    :id="selected"
                    :url="linksUrl"
                    direction="UD"
                    level-separation="100"
                    sort-method="directed"
                    hierarchical
                />
            </div>
        </div>
    </div>
</template>

<script>
import sideMenu from '@/sideMenu.vue'
import graphicalRepresentation from '@/graphs/graphicalRepresentation.vue'

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
        },
        linksActive: {
            type: Boolean,
            default: false
        }
    },
    components: {
        'side-menu': sideMenu,
        'graph': graphicalRepresentation,
    },
    data: () => ({
        selected: 0
    }),
    computed: {
        menuItems: function() {
            let items = ['General', 'Supersedes']
            if (this.linksActive) {
                items.push('Links')
            }
            return items
        }
    }
}
</script>

<style>
.graphs-content {
    margin-top: 15px
}
</style>
