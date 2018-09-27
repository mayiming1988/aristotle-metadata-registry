const webpack = require('webpack')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = (config) => {
  config.set({
    // ... normal karma configuration
    files: [
      // all files ending in "_test"
      { pattern: 'test/*_test.js', watched: false },
      { pattern: 'test/**/*_test.js', watched: false }
      // each file acts as entry point for the webpack configuration
    ],
    preprocessors: {
      // add webpack as preprocessor
      'test/*_test.js': [ 'webpack' ],
      'test/**/*_test.js': [ 'webpack' ]
    },
    frameworks: ['mocha'],
    browsers: ['PhantomJS'],
    webpack: {
      // karma watches the test entry points
      // (you don't need to specify the entry option)
      // webpack watches dependencies

      // webpack configuration
      module: {
        rules: [
          {
            // Load .vue files with vue-loader
            test: /\.vue$/,
            use: 'vue-loader'
          },
          {
            test: /\.m?js$/,
            exclude: /node_modules/,
            use: [{
              loader: 'babel-loader',
              options: {
                presets: ['@babel/preset-env']
              }
            },{
              loader: 'eslint-loader'
            }]
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
