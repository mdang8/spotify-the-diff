const path = require('path');

module.exports = {
  entry: [
    'babel-polyfill',
    path.resolve(__dirname, './src/client/app.js'),
  ],
  output: {
    path: path.resolve(__dirname, 'public'),
    filename: 'bundle.js',
    publicPath: '/',
  },
  devtool: '#eval-source-map',
  module: {
    rules: [
      {
        test: /(\.css|.scss)$/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      },
      {
        test: /\.(jsx|js)?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
              presets: ['@babel/preset-env', '@babel/preset-react']
            }
          }
        ],
      }
    ],
  },
  resolve: {
    extensions: ['*', '.js', '.jsx']
  },
};
