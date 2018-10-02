const webpack = require('webpack')
const path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = (config) => {
  config.set({
    frameworks: ['mocha'],
    browsers: ['PhantomJS'],
    files: [
      // all files ending in "_test"
      { pattern: 'test/*_test.js', watched: false },
      { pattern: 'test/**/*_test.js', watched: false }
      // each file acts as entry point for the webpack configuration
    ],
    preprocessors: {
      // add webpack as preprocessor
      'test/*_test.js': [ 'webpack', 'sourcemap' ],
      'test/**/*_test.js': [ 'webpack', 'sourcemap' ]
    },
    webpack: {
      // karma watches the test entry points
      // (you don't need to specify the entry option)
      // webpack watches dependencies

      // webpack configuration
      devtool: 'inline-source-map',
      module: {
        rules: [
          {
            // Load .vue files with vue-loader
            test: /\.vue$/,
            use: 'vue-loader'
          },
          {
            test: /\.m?js$/,
            exclude: /node_modules\/(?!(vue-simple-suggest|sinon))/,
            use: [{
              loader: 'babel-loader',
              options: {
                presets: ['@babel/preset-env']
              }
            }]
          },
          {
            test: /\.css$/,
            use: [
              'style-loader',
              'css-loader'
            ]
          }
        ]
      },
      plugins: [
        new VueLoaderPlugin(),
        new webpack.ProvidePlugin({
          // Provide $ and jQuery to scripts, no need to import
          $: "jquery",
          jQuery: "jquery"
        }),
      ]
    },
    webpackMiddleware: {
      // webpack-dev-middleware configuration
      // i. e.
      stats: 'errors-only'
    }
  })
}
