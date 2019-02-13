<template>
  <div :hidden="!show" class="panel panel-default" style="margin:0 10%;">
      <div class="panel-heading">
          <h3 class="panel-title">Graphical representation</h3>
      </div>
      <div id="network" class="panel-body" style="height:450px;"></div>
      <div id="legend" class="panel-footer">
          <ul>
          <li>Ovals indicate instances of different relationships, Rectangles indicate different
          metadata objects within a link.</li>
          <li>Select a relationship to see all metadata objects in that relationship.</li>
          <li>Hover over a line to see the role a metadata item fills within a relationship</li>
      </ul>
      </div>
  </div>
</template>

<script>
export default {
    props: ['url'],
    data: () => ({
        show: false
    }),
    mounted: function() {
        $.getJSON(this.url, (data) => {
            // Import vis async just before we need it. It's a big library
            import('vis').then((vis) => {
                let nodes = new vis.DataSet(data['nodes']);
                let edges = new vis.DataSet(data['edges']);

                // create a network
                let container = document.getElementById('network');
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
                            'sortMethod': 'directed'
                        }
                    }
                };
                new vis.Network(container, final_data, options);

                // Now show the component
                if (!this.show) {
                    this.show = true
                }
            })
        })
    }
}
</script>

<style>
@import '../../node_modules/vis/dist/vis.css';
</style>
