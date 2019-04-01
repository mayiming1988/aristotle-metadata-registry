<template>
    <div>
        <p v-if="!ready">
            <i class="fa fa-spinner fa-pulse" /> Please wait, we are preparing the graph.
        </p>
        <alert v-if="error" type="danger">
            There was an error with the graph. Please try again later
        </alert>
        <div :id="id" class="vis-canvas" />
    </div>
</template>

<script>
import Alert from 'uiv/src/components/alert/Alert.vue'
import apiRequest from 'src/mixins/apiRequest.js'

export default {
    data: () => ({
        ready: false,
        error: false,
        nodes: {},
        edges: {}
    }),
    mixins: [apiRequest],
    props: {
        id: {
            type: Number,
            default: 0
        },
        url: {
            type: String,
            required: true
        },
        // This property needs to be removed and replaced with actual options being varied
        typeOfGraph: {
            type: String,
            default: 'general'
        },
        direction: {
            type: String,
            required: true
        },
        levelSeparation: {
            type: String,
            required: true
        },
        hierarchical: {
            type: Boolean,
            default: false
        },
        showType: {
            type: Boolean,
            default: false
        },
        sortMethod: {
            type: String,
            required: true
        },
        startActive: {
            type: Boolean,
            default: true
        }
    },
    components: {
        'alert': Alert
    },
    name: "graphicalRepresentation",
    mounted: function() {
        // Build graph when component is first mounted
        this.buildGraph()
    },
    methods: {
        buildGraph: function () {
            this.get(this.url).then((response) => {

                this.nodesProcessor(response.data.nodes)
                this.edgesProcessor(response.data.edges)

                import('vis').then((vis) => {

                    this.nodes = response.data.nodes
                    this.edges = response.data.edges

                    let nodes = new vis.DataSet(this.nodes);
                    let edges = new vis.DataSet(this.edges);

                    // create a network
                    let container = document.getElementById(this.id);
                    let final_data = {
                        nodes: nodes,
                        edges: edges
                    };
                    let options = {
                        "clickToUse": true,
                        "nodes": {
                            "shape": 'box',
                            "borderWidth": 2,
                            "margin": 3,
                            "font": {
                                // "face": "Courier",
                                "size": 15
                            }
                        },
                        "edges": {
                            "chosen": false,
                        },
                        "interaction": {
                            "hover": true,
                            "tooltipDelay": 0,
                            "selectConnectedEdges": false
                        },
                        'layout': {
                            'hierarchical': {
                                'enabled': this.hierarchical,
                                'direction': this.direction,
                                'sortMethod': this.sortMethod,
                                'levelSeparation': Number(this.levelSeparation)
                            }
                        }
                    };
                    let network = new vis.Network(container, final_data, options);

                    if (this.startActive) {
                        // Make the vis.js canvas "active" as soon as the page is loaded:
                        let canvas = document.getElementsByClassName('vis-network')[0]
                        let overlay = document.getElementsByClassName('vis-overlay')[0]
                        
                        canvas.onmouseenter = function() {
                            canvas.classList.add("vis-active")
                            overlay.style.display = "none"
                        }
                        
                        canvas.onmouseleave = function() {
                            canvas.classList.remove("vis-active")
                            overlay.style.display = "block"
                        }
                    }

                    // Disable the physics as soon as the vis.js is loaded:
                    network.on("stabilizationIterationsDone", function () {
                        network.setOptions({physics: false})
                    })

                    network.on('hoverNode', function () {
                        document.body.style.cursor = 'pointer'

                    });

                    network.on('blurNode', function () {
                        document.body.style.cursor = 'default'
                    })


                    network.on('doubleClick', function (net) {
                        if (net.nodes.length > 0) {
                            let nodesArray = nodes.get(net.nodes)
                            let myNode = nodesArray[0]
                            window.location.href = myNode.absolute_url
                        }
                        if (net.edges.length > 0) {
                            let edgesArray = edges.get(net.edges)
                            let myEdge = edgesArray[0]
                            window.location.href = myEdge.absolute_url
                        }
                    })

                    network.on('showPopup', function () {
                        document.body.style.cursor = 'pointer'
                    })

                    network.on('hidePopup', function () {
                        document.body.style.cursor = 'default'
                    })
                    this.ready = true
                })
            })
        },
        sentenceTrimmer: function (sentence) {
            const maximumLength = 30
            let firstString
            let lastString = ""
            let indexOfSpace
            if (sentence.length <= maximumLength) { return sentence; }
            firstString = sentence.slice(0, maximumLength)
            indexOfSpace = Math.min(firstString.length, firstString.lastIndexOf(" "))

            if (sentence.length <= maximumLength * 2) {
                firstString = firstString.substr(0, indexOfSpace) + "\n"
                lastString = sentence.slice(indexOfSpace + 1, maximumLength * 2)
                return firstString + lastString
            } else {
                firstString = firstString.substr(0, indexOfSpace) + "\n"
                let secondString = sentence.slice(indexOfSpace + 1, indexOfSpace + 1 + maximumLength)
                let indexOfSpaceSecondString = Math.min(secondString.length, secondString.lastIndexOf(" "))
                secondString = secondString.slice(0, indexOfSpaceSecondString) + "…\n"
                lastString = sentence.slice(-maximumLength)
                indexOfSpace = lastString.indexOf(" ")
                lastString = "…" + lastString.slice(indexOfSpace + 1)
                return firstString + secondString + lastString
            }

        },
        sentenceTrimmerSingleLine: function (sentence) {
            const maximumLength = 20
            if (sentence.length <= maximumLength) { return sentence; }
            return sentence.slice(0, maximumLength) + "…"
        },
        nodesProcessor: function (responseNodes) {
            for (let element of responseNodes) {
                    element.title = `<small>Name: ${element.name}</small><br>`
                    if (element.short_definition !== "") {
                        element.title = element.title.concat(`<small>Definition: ${element.short_definition}</small><br>`)
                    }
                    if (element.version !== "" && element.version !== undefined) {
                        element.title = element.title.concat(`<small>Version: ${element.version}</small>`)
                    }
                    if (this.typeOfGraph === "supersedes") {
                        element.label = this.sentenceTrimmer(element.name)
                    } else if (this.typeOfGraph === "general") {
                        element.label = this.sentenceTrimmer(element.name)
                        // If we want to show type add to label
                        if (this.showType) {
                            element.label += " \n(" + element.type + ")"
                        }
                    }

                    if (element.node_options) {
                        element.shape = element.node_options.shape
                        element.borderWidth = element.node_options.borderWidth
                        element.margin = element.node_options.margin
                        element["font"] = {}
                        element.font.size = element.node_options.font.size
                        element.color = '#ffc05d'
                    }
                }
        },
        edgesProcessor: function (responseEdges) {

            let edges = []

            for (let element of responseEdges) {

                let roundness

                if (this.typeOfGraph === "supersedes") {
                    element.label = this.sentenceTrimmerSingleLine(element.registration_authority)
                    element.title = `<small>Superseding registration authority: ${element.registration_authority}</small>`
                    element.from = element.older_item
                    element.to = element.newer_item
                    element.font = {align: "top", face: "Helvetica", color: "black"}
                    element.smooth = {"enabled": true, "type": "curvedCCW", "roundness": 0.2}
                    roundness = 0.35
                } else if (this.typeOfGraph === "general") {
                    element.smooth = {"enabled": true, "type": "curvedCCW", "roundness": 0}
                    roundness = 0
                }
                element.arrows = "to"

                // If the edge is "duplicated"
                // (e.g. two or more edges have the same 'from' and 'to' values)
                // Change the roundness of the curvature so they don't overlap:
                for (let i = 0; i < edges.length; i++) {
                    // Comparing the "stringified" version of two object is the most performance efficient:
                    if (JSON.stringify(edges[i]) === JSON.stringify({"from": element.from, "to": element.to})) {
                        element.smooth = {"enabled": true, "type": "curvedCCW", "roundness": roundness}
                        roundness += 0.15
                    }
                }
                edges.push({"from": element.from, "to": element.to})
            }
        }
    },
    watch: {
        url: function() {
            // Rebuild the graph if url is changed
            this.buildGraph()
        }
    }
}
</script>

<style>
.vis-canvas {
    height: 400px;
    width: 100%;
    border-color: #d2d2d2;
    border-style: solid; 
    border-width: thin
}
</style>
