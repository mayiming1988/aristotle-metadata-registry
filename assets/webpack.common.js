/* eslint-env node */
const path = require('path')
const webpack = require('webpack')
const entry = require('webpack-glob-entry')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const MiniCssExtractPlugin = require("mini-css-extract-plugin")
const BundleTracker  = require('webpack-bundle-tracker')
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin

const entries = entry('./src/pages/*.js', './src/pages/**/*.js', './src/custom/entry/*.js')

module.exports = {
    entry: entries,
    output: {
        filename: '[name]-[contenthash].bundle.js',
        chunkFilename: '[name]-[contenthash].bundle.js',
        path: path.resolve(__dirname, 'dist/bundles'),
        hashDigest: 'hex',
        hashDigestLength: 16,
        hashFunction: 'sha256'
    },
    module: {
        strictExportPresence: true,  // Missing exports fail the build
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
                // Load .js and .mjs files with babel
                test: /\.m?js$/,
                exclude: /node_modules\/(?!(vue-simple-suggest|uiv))/, //Don't run on node modules except these
                use: [{
                    loader: 'babel-loader',
                    options: {
                        presets: [
                            [
                                '@babel/preset-env',
                                {
                                    useBuiltIns: 'entry',
                                    modules: false,
                                    corejs: '2'
                                }
                            ]
                        ],
                        plugins: ["@babel/plugin-syntax-dynamic-import"],
                    }
                }]
            },
            {
                // Compile less and process css
                test: /\.less$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader
                    },
                    {
                        loader: 'css-loader',
                        options: {
                            modules: 'global',
                            importLoaders: 1
                        }
                    },
                    {
                        loader: 'less-loader'
                    }
                ]
            },
            {
                // Process and extract
                test: /\.css$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader
                    },
                    {
                        loader: 'css-loader',
                        options: {modules: 'global'}
                    }
                ]
            },
            {
                test: /\.(woff2?|ttf|eot|svg|png|jpg)$/,
                use: [{
                    loader: 'file-loader',
                    options: {
                        name: '[name]-[sha256:hash:hex:16].[ext]'
                    }
                }]
            },
        ]
    },
    plugins: [
        // Clean dist folder before builds
        new CleanWebpackPlugin(),
        // Load .vue files
        new VueLoaderPlugin(),
        // Provide $ and jQuery to scripts, no need to import
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery"
        }),
        // Ignore all locale files of moment.js
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
        // Extract css to .css files
        new MiniCssExtractPlugin({
            filename: '[name]-[contenthash].bundle.css'
        }),
        /*
         * Creates json file with bundle information
         * Required for django-webpack-loader
         */
        new BundleTracker({
            path: __dirname, 
            filename: './dist/webpack-stats.json'
        }),
        // Create report.html
        new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            openAnalyzer: false
        })
    ],
    optimization: {
        // How bundle are split into files
        splitChunks: {
            cacheGroups: {
                vendors: {
                    chunks: 'async',
                    test: /[\\/]node_modules[\\/]/,
                },
                common: {
                    name: 'common',
                    chunks: 'all',
                    minChunks: Object.keys(entries).length - 1
                },
            }
        }
    },
    // Uses external variables instead of including packages
    externals: {
        esprima: 'esprima' // This is being used to exclude esprima from bundle since we dont need it
    },
    resolve: {
        alias: {
            // Use compiler version of vue
            'vue$': 'vue/dist/vue.esm.js',
            'src': path.resolve(__dirname, 'src'),
            '@': path.resolve(__dirname, 'src/components'),
        }
    }
};
