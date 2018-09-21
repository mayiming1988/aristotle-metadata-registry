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
  module: {
    rules: [{
      test: require.resolve('jquery'),
      use: [{
        // Expose jquery outside bundle
        loader: 'expose-loader',
        options: '$'
      },{
        loader: 'expose-loader',
        options: 'jQuery'
      }]
    }]
  },
  plugins: [
    new webpack.ProvidePlugin({
      // Provide $ and jQuery to scripts, no need to import
      $: "jquery",
      jQuery: "jquery"
    })
  ]
};
