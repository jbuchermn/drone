const webpack = require('webpack');
const config = {
    entry:  __dirname + '/js/index.js',
    output: {
        path: __dirname + '/dist',
        filename: 'bundle.js',
    },
    resolve: {
        extensions: ['.mjs', '.js', '.jsx', '.css']
    },
    module: {
      rules: [
        {
          test: /\.jsx?/,
          exclude: /node_modules/,
          use: 'babel-loader'
        },
        {
		  test: /\.css$/,
		  use: ['style-loader', 'css-loader']
		}
      ]
    },
    node: {
      fs: "empty"
    }
};
module.exports = config;
