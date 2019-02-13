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

                data.nodes.forEach(function (element) {
                    element.title = "hello world <br> <div>hiiii</div>"
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
                            "hover": true,
                            "tooltipDelay": 1
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

                    network.on("stabilizationIterationsDone", function () {
                        network.setOptions({physics: false})
                    })

                    // network.on("hoverNode", function (node) {
                    //     console.log(node)
                    // })

                    network.on('hoverNode', function (properties) {
                        console.log(properties)
                        var nodeID = properties.node;
                        if (nodeID) {

                            var sNodeLabel = this.body.nodes[nodeID].options.label
                            var sToolTip = this.body.nodes[nodeID].options.title;

                            //use JQUERY to see where the canvas is on the page.
                            var canvasPosition = $('.vis-network').position();

                            //the properties give x & y relative to the edge of the canvas, not to the whole document.
                            var clickX = properties.pointer.DOM.x + canvasPosition.top;
                            var clickY = properties.pointer.DOM.y + canvasPosition.left;

                            //make sure we have a valid div, either clear it or generate one.
                            if ($('#cellBatchAttrPopUp').length) {
                                $('div#cellBatchAttrPopUp').empty();
                            }
                            else {
                                $('<div id="cellBatchAttrPopUp"></div>').click(function () {
                                    //clicking the popup hides it again.
                                    $(this).empty().hide();
                                }).css('position','absolute').appendTo("body");
                            }

                            // put the div over the node, display the tooltip and show it.
                            $('div#cellBatchAttrPopUp').append(sNodeLabel)
                                .append('<br/>')
                                .append(sToolTip)
                                .css('top', clickY).css('left', clickX)
                                .show();

                        }
                    });

                })
            })
        }
    }
</script>

<style scoped>
    div#cellBatchAttrPopUp {
    display: none;
    position: absolute;
    z-index: 2000;
    padding: 4px 8px;
    color: #333;
    white-space: nowrap;
    -moz-border-radius: 5px;
    -webkit-border-radius: 5px;
    border-radius: 5px;
    -moz-box-shadow: 0px 0px 4px #222;
    -webkit-box-shadow: 0px 0px 4px #222;
    box-shadow: 0px 0px 4px #222;
    background-image: -moz-linear-gradient(top, #eeeeee, #cccccc);
    background-image: -webkit-gradient(linear,left top,left bottom,color-stop(0, #eeeeee),color-stop(1, #cccccc));
    background-image: -webkit-linear-gradient(top, #eeeeee, #cccccc);
    background-image: -moz-linear-gradient(top, #eeeeee, #cccccc);
    background-image: -ms-linear-gradient(top, #eeeeee, #cccccc);
    background-image: -o-linear-gradient(top, #eeeeee, #cccccc);
}
</style>