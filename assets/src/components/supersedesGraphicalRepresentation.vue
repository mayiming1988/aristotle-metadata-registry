<template>
    <div id="network-id" style="height: 400px; width: 100%">
    </div>
</template>

<script>
    import { Alert } from 'uiv'
    import apiRequest from 'src/mixins/apiRequest.js'

    export default {
        mixins: [apiRequest],
        props: {
            url: String
        },
        components: {
            'alert': Alert
        },
        name: "supersedesGraphicalRepresentation",
        mounted() {
            this.buildGraph()
        },
        methods: {
            buildGraph: function () {
                this.get(this.url).then((response) => {
                    for (let element of response.data.nodes) {
                        element.title = `<small>Name: ${element.name}</small><br>`
                        if (element.definition !== "") {
                            element.title = element.title.concat(`<small>Definition: ${element.short_definition}</small><br>`)
                        }
                        if (element.version !== "") {
                            element.title = element.title.concat(`<small>Version: ${element.version}</small>`)
                        }
                        element.label = element.name
                        if (element.node_options) {
                            element.shape = element.node_options.shape
                            element.borderWidth = element.node_options.borderWidth
                            element.margin = element.node_options.margin
                            element["font"] = {}
                            element.font.size = element.node_options.font.size
                            element.color = '#ffc05d'
                        }
                        delete element.name
                    }

                    let edges = []

                    for (let element of response.data.edges) {
                        element.label = element.registration_authority
                        element.from = element.older_item
                        element.to = element.newer_item
                        delete element.older_item
                        delete element.newer_item
                        delete element.registration_authority
                        element.font = {align: "top", face: "Helvetica", color: "black"}
                        element.arrows = "to"

                        element.smooth = {"enabled": true, "type": "curvedCCW", "roundness": 0.2}

                        // If the edge is "duplicated"
                        // (e.g. two or more edges have the same 'from' and 'to' values)
                        // Change the roundNess of the curvature so they don't overlap:
                        let roundess = 0.35
                        for (let i = 0; i < edges.length; i++) {
                            // Comparing the "stringified" version of two object is the most performance efficient:
                            if (JSON.stringify(edges[i]) === JSON.stringify({"from": element.from, "to": element.to})) {
                                element.smooth = {"enabled": true, "type": "curvedCCW", "roundness": roundess}
                                roundess += 0.15
                            }
                        }
                        edges.push({"from": element.from, "to": element.to})
                    }

                    import('vis').then((vis) => {

                        let nodes = response.data.nodes
                        let edges = response.data.edges

                        nodes = new vis.DataSet(nodes);
                        edges = new vis.DataSet(edges);

                        // create a network
                        let container = document.getElementById('network-id');
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
                                    "size": 17
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
                                    'enabled': true,
                                    'direction': 'LR',
                                    'sortMethod': 'directed',
                                    // 'sortMethod': 'hubsize',
                                    'levelSeparation': 300
                                }
                            }
                        };
                        let network = new vis.Network(container, final_data, options);

                        // // Make the vis.js canvas "active" as soon as the page is loaded:
                        // let canvas = document.getElementsByClassName('vis-network')[0]
                        // let overlay = document.getElementsByClassName('vis-overlay')[0]
                        //
                        // canvas.onmouseenter = function() {
                        //     canvas.classList.add("vis-active")
                        //     overlay.style.display = "none"
                        // }
                        //
                        // canvas.onmouseleave = function() {
                        //     canvas.classList.remove("vis-active")
                        //     overlay.style.display = "block"
                        // }

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


                        network.on('click', function (net) {
                            if (net.nodes.length > 0) {
                                let nodesArray = nodes.get(net.nodes)
                                let myNode = nodesArray[0]
                                window.location.href = myNode.absolute_url
                            }
                        })

                        network.on('showPopup', function () {
                            document.body.style.cursor = 'pointer'
                        })

                        network.on('hidePopup', function () {
                            document.body.style.cursor = 'default'
                        })
                    })
                })
            }
        }
    }
</script>

<style scoped>

</style>