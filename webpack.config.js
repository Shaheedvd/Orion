const path = require('path')

module.exports = {
  entry: './src/main.jsx',
  output: {
    path: path.resolve(__dirname, 'src'),
    filename: 'main.js'
  },
  module: {
    rules: [
      { test: /\.jsx?$/, exclude: /node_modules/, use: { loader: 'babel-loader', options: { presets:['@babel/preset-react'] } } },
      { test: /\.css$/, use: ['style-loader','css-loader'] }
    ]
  },
  resolve: { extensions: ['.js','.jsx'] }
}
