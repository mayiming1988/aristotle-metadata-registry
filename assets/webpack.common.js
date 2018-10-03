const path = require('path')
const webpack = require('webpack')
const glob = require('glob')
const entry = require('webpack-glob-entry')
const CleanWebpackPlugin = require('clean-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const MiniCssExtractPlugin = require("mini-css-extract-plugin")
var BundleTracker  = require('webpack-bundle-tracker')

const entries = entry('./src/pages/*.js')

module.exports = {
  entry: entries,
  output: {
    filename: '[name]-[Contenthash].js',
    path: path.resolve(__dirname, 'dist/bundles'),
  },
  module: {
    rules: [
      {
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
      },
      {
        // Load .vue files with vue-loader
        test: /\.vue$/,
        use: 'vue-loader'
      },
      {
        test: /\.m?js$/,
        exclude: /node_modules\/(?!vue-simple-suggest)/,
        use: [{
          loader: 'babel-loader',
          options: {
            presets: [
              [
                '@babel/preset-env',
                {
                  useBuiltIns: 'entry'
                }
              ]
            ]
          }
        }]
          //loader: 'eslint-loader',
          //options: {
          //  failOnError: false,
          //  failOnWarning: false
          //}
      },
      {
        test: /\.woff2?$|\.ttf$|\.eot$|\.svg$/,
        use: [{
          loader: 'file-loader',
          options: {
            name: '[name].[ext]'
          }
        }]
      },
      {
        test: /\.less$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'less-loader'
        ]
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader"
        ]
      }
    ]
  },
  plugins: [
    // Clean dist folder before builds
    new CleanWebpackPlugin(['dist']),
    new VueLoaderPlugin(),
    new webpack.ProvidePlugin({
      // Provide $ and jQuery to scripts, no need to import
      $: "jquery",
      jQuery: "jquery"
    }),
    new MiniCssExtractPlugin({
      filename: '[name]-[contenthash].css'
    }),
    new BundleTracker({
      path: __dirname, 
      filename: './dist/webpack-stats.json'
    })
  ],
  optimization: {
    splitChunks: {
      cacheGroups: {
        common: {
          name: 'common',
          chunks: 'all',
          minChunks: Object.keys(entries).length - 1
        }
      }
    }
  },
  resolve: {
    alias: {
      // Use compiler version of vue
      'vue$': 'vue/dist/vue.esm.js'
    }
  }
};
