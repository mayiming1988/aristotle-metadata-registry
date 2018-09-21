const path = require('path');
var webpack = require('webpack')

module.exports = {
  entry: {
    base: './src/base.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist/bundles'),
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    })
  ]
};
