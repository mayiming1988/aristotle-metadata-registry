<template>
    <div id="network-id" style="height: 400px; width: 100%">
    </div>
</template>

<script>

    export default {
        props: ['url'],
        name: "graphicalRepresentation",
        mounted() {
            $.getJSON(this.url, (data) => {
                console.log(data.nodes)
                console.log(data.edges)
                let linkdata = data

                data.nodes.forEach(function (element) {
                    element.title = "hello world"
                    element.label = element.name
                    delete element.name
                    console.log(element)
                })

                data.edges.forEach(function (element) {
                    element.label = element.registration_authority
                    element.from = element.older_item
                    element.to = element.newer_item
                    element.smooth = {enabled: true, type: 'curvedCCW', roundness: 0.3}
                    delete element.older_item
                    delete element.newer_item
                    delete element.registration_authority
                    element.font = {align: "top", face: "Helvetica", color: "black"}
                    element.arrows = "to"
                })

                import('vis').then((vis) => {

                    var nodes = data.nodes
                    var edges = data.edges

                    // var nodes = [
                    //     {id: 1, label: "Node 1"},
                    //     {id: 2, label: "Node 2"},
                    //     {id: 3, label: "Node 3:\nLeft-Aligned", font: {'face': "Monospace", align: 'left'}},
                    //     {id: 4, label: "Node 4"},
                    //     {id: 5, label: "Node 5:\nLeft-Aligned box", shape: 'box', font: {'face': "Monospace", align: 'left'}},
                    // ];
                    //
                    // var edges = [
                    //     {from: 1, to: 2, label: 'middle', font: {align: 'middle'}, arrows: 'to'},
                    //     {from: 1, to: 3, label: 'top', font: {align: 'top'}, arrows: 'to'},
                    //     {from: 2, to: 4, label: 'horizontal', font: {align: 'horizontal'}, arrows: 'to'},
                    //     {from: 2, to: 5, label: 'bottom', font: {align: 'bottom'}, arrows: 'to'},
                    //     {from: 4, to: 1, label: 'bottom', font: {align: 'bottom'}, arrows: 'to'},
                    // ];

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
                            "shape": 'box'

                        },
                        "interaction": {
                        },
                        "groups": {
                            "active": {
                                "color": {border:'black'},
                                "font": {size:18},
                                "shape": 'box'
                            },
                            "regular": {
                                "font": {size:15},
                                "shape": 'box'
                            },
                            "relation": {
                                "font": {size:15},
                                "shape": 'ellipse'
                            },
                        },
                        'layout': {
                            'hierarchical': {
                                'enabled': true,
                                'direction': 'LR',
                                'sortMethod': 'directed',
                                'levelSeparation': 300
                            }
                        }
                    };
                    let network = new vis.Network(container, final_data, options);

                    // Now show the component
                    if (!this.show) {
                        this.show = true
                    }

                    network.on("stabilizationIterationsDone", function () {
                        network.setOptions({physics: false})
                    })
                })
            })
        }
    }
</script>

<style scoped>

</style>