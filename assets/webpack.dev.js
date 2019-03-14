/* eslint-env node */
const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    output: {
        publicPath: '/static/bundles/',
    },
    mode: 'development',
    devtool: 'inline-source-map',
    watchOptions: {
        ignored: /node_modules/
    }
})
