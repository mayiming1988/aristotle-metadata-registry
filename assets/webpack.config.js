const path = require('path');

module.exports = {
  entry: {
    base: './src/base.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist')
  }
};
