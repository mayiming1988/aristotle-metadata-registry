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

                data.nodes.forEach(function (element) {
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
                        element["font"] ={}
                        element.font.size = element.node_options.font.size
                        element.color = '#ffc05d'
                    }
                    delete element.name
                })

                let edges = []

                data.edges.forEach(function (element) {
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
                })

                import('vis').then((vis) => {

                    let nodes = data.nodes
                    let edges = data.edges

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
                                // 'sortMethod': 'directed',
                                'sortMethod': 'hubsize',
                                'levelSeparation': 300
                            }
                        }
                    };
                    let network = new vis.Network(container, final_data, options);

                    // Make the vis.js canvas "active" as soon as the page is loaded:
                    let canvas = document.getElementsByClassName('vis-network')[0]
                    let overlay = document.getElementsByClassName('vis-overlay')[0]

                    // Disable the physics as soon as the vis.js is loaded:
                    network.on("stabilizationIterationsDone", function () {
                        network.setOptions({physics: false})
                    })

                    canvas.onmouseenter = function() {
                        canvas.classList.add("vis-active")
                        overlay.style.display = "none"
                    }

                    canvas.onmouseleave = function() {
                        canvas.classList.remove("vis-active")
                        overlay.style.display = "block"
                    }


                    // network.on("hoverNode", function (node) {
                    //     console.log(node)
                    // })

                    // THIS HACKY SOLUTION SOLVES A WEIRD BUG:
                    // FOR LARGE NETWORKS, SOMETIMES THE LABELS ARE NOT APPEARING IN THE CORRECT POSITIONS
                    // network.on("afterDrawing", function () {
                    //
                    //     // console.log("THESE ARE THE EDGES:")
                    //     // console.log(networkNodes.body.edges)
                    //     // Object.values(networkNodes.body.nodes).forEach(function (node) {
                    //     //     network.moveNode(node.id, node.x, node.y + 1)
                    //     // })
                    // })

                    network.on('hoverNode', function() {
                        // console.log(properties)
                        // var nodeID = properties.node;
                        // if (nodeID) {
                        //
                        //     var sNodeLabel = this.body.nodes[nodeID].options.label
                        //     var sToolTip = this.body.nodes[nodeID].options.title;
                        //
                        //     //use JQUERY to see where the canvas is on the page.
                        //     var canvasPosition = $('.vis-network').position();
                        //
                        //     //the properties give x & y relative to the edge of the canvas, not to the whole document.
                        //     var clickX = properties.pointer.DOM.x + canvasPosition.top;
                        //     var clickY = properties.pointer.DOM.y + canvasPosition.left;
                        //
                        //     //make sure we have a valid div, either clear it or generate one.
                        //     if ($('#cellBatchAttrPopUp').length) {
                        //         $('div#cellBatchAttrPopUp').empty();
                        //     }
                        //     else {
                        //         $('<div id="cellBatchAttrPopUp"></div>').click(function () {
                        //             //clicking the popup hides it again.
                        //             $(this).empty().hide();
                        //         }).css('position','absolute').appendTo("body");
                        //     }
                        //
                        //     // put the div over the node, display the tooltip and show it.
                        //     $('div#cellBatchAttrPopUp').append(sNodeLabel)
                        //         .append('<br/>')
                        //         .append(sToolTip)
                        //         .css('top', clickY).css('left', clickX)
                        //         .show();
                        // }
                        document.body.style.cursor = 'pointer'

                    });

                    network.on('blurNode', function() {
                        document.body.style.cursor = 'default'
                    })


                    network.on('click', function(net) {
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
                        document.body.style.cursor ='default'
                    })
                })
            })
        }
    }
</script>

<style scoped>
    /*div#cellBatchAttrPopUp {*/
        /*display: none;*/
        /*position: absolute;*/
        /*z-index: 2000;*/
        /*padding: 4px 8px;*/
        /*color: #333;*/
        /*white-space: nowrap;*/
        /*-moz-border-radius: 5px;*/
        /*-webkit-border-radius: 5px;*/
        /*border-radius: 5px;*/
        /*-moz-box-shadow: 0px 0px 4px #222;*/
        /*-webkit-box-shadow: 0px 0px 4px #222;*/
        /*box-shadow: 0px 0px 4px #222;*/
        /*background-image: -moz-linear-gradient(top, #eeeeee, #cccccc);*/
        /*background-image: -webkit-gradient(linear,left top,left bottom,color-stop(0, #eeeeee),color-stop(1, #cccccc));*/
        /*background-image: -webkit-linear-gradient(top, #eeeeee, #cccccc);*/
        /*background-image: -moz-linear-gradient(top, #eeeeee, #cccccc);*/
        /*background-image: -ms-linear-gradient(top, #eeeeee, #cccccc);*/
        /*background-image: -o-linear-gradient(top, #eeeeee, #cccccc);*/
    /*}*/
</style>