const tailwindcss = require('@tailwindcss/postcss') // nuevo plugin

module.exports = {
  plugins: [
    tailwindcss(),
    require('autoprefixer'),
  ],
}
