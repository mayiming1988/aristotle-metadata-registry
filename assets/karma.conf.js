const webpack = require('webpack')
const path = require('path')
const VueLoaderPlugin = require('vue-loader/lib/plugin')

process.env.CHROME_BIN = require('puppeteer').executablePath()

module.exports = (config) => {
    config.set({
        frameworks: ['mocha'],
        browsers: ['ChromeHeadlessNoSandbox'],
        customLaunchers: {
            // Need this for travis container environment
            ChromeHeadlessNoSandbox: {
                base: 'ChromeHeadless',
                flags: ['--no-sandbox']
            }
        },
        reporters: ['mocha'],
        mochaReporter: {
            colors: {
                success: 'green',
                info: 'blue',
                warning: 'yellow',
                error: 'red'
            }
        },
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
            optimization: {
                minimize: false
            },
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
