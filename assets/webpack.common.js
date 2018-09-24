const path = require('path')
const webpack = require('webpack')
const glob = require('glob')
const entry = require('webpack-glob-entry')

module.exports = {
  entry: entry('./src/pages/*.js'),
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist/bundles'),
  },
  module: {
    rules: [{
      // Expose jquery outside bundle
      // Wont need this when using only bundle code
      test: require.resolve('jquery'),
      use: [{
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
