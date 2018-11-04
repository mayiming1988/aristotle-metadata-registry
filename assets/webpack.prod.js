const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const webpack = require('webpack')

const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");

// Try the environment variable, otherwise use static
const ASSET_PATH = process.env.ASSET_PATH || '/static/bundles/';
console.log('ASSET_PATH: ', ASSET_PATH)

module.exports = merge(common, {
    mode: 'production',
    output: {
        publicPath: ASSET_PATH
    },
    optimization: {
        minimizer: [
            new UglifyJsPlugin(),
            new OptimizeCSSAssetsPlugin()
        ]
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.ASSET_PATH': JSON.stringify(ASSET_PATH)
        })
    ]
})
