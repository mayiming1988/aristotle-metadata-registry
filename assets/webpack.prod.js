/* eslint-env node */
const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const webpack = require('webpack')

const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const TerserPlugin = require('terser-webpack-plugin');

// Try the environment variable, otherwise use static
const ASSET_PATH = process.env.ASSET_PATH || '/static/bundles/';
console.log('ASSET_PATH: ', ASSET_PATH)

module.exports = merge(common, {
    mode: 'production',
    output: {
        publicPath: ASSET_PATH
    },
    devtool: 'source-map',
    optimization: {
        minimizer: [
            new TerserPlugin({
                sourceMap: true
            }),
            new OptimizeCSSAssetsPlugin()
        ],
        noEmitOnErrors: true,
        usedExports: true,
        sideEffects: true,
        concatenateModules: true,
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.ASSET_PATH': JSON.stringify(ASSET_PATH)
        })
    ]
})
