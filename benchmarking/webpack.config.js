const path = require('path');
const webpack = require('webpack');
const env = process.env.NODE_ENV;
const CopyWebpackPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const addPlugins = (plugins) =>  plugins.forEach(plugin => config.plugins.push(plugin));

const isProduction = env === 'production';
const PORT = process.env.PORT || 9182;


const exportHtmlConfig = {
    minimize: isProduction===true,
    inject: 'head'
};

var config = {
    entry: {
        main: path.resolve(__dirname, 'src/index.js'),
    },
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].[hash:20].js'
    },
    devServer: {
        contentBase: path.join(__dirname, 'src'),
        watchContentBase: true,
        port: PORT,
        hot: false
    },
    node: {
        fs: 'empty'
    },
    module: {
        rules: [
            {
                loader: 'url-loader',
                test: /\.(ttf|svg|eot|woff|woff2|png|gif|jpg|jpeg)$/,
                options: {
                    limit: 20000,
                    name: 'assets/[sha512:hash:base64:7].[ext]'
                }

            },
            {
                test: /\.(css|scss)$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.html$/,
                loader: 'html-loader'
            }
        ]
    },
    plugins: []
};


addPlugins([
    new CopyWebpackPlugin([
        { from: './src/images/', to: './images/' }
    ])
]);

addPlugins([
    new HtmlWebpackPlugin({
        ...exportHtmlConfig,
        template: `./src/index.html`,
        chunks: ['main'],
        inject: 'body'
    })
])

module.exports = config;
