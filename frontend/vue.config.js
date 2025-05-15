const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  // 禁用ESLint
  lintOnSave: false,
  transpileDependencies: true,
  // 开发服务器配置
  devServer: {
    // 设置端口为8080
    port: 8080,
    // 设置主机为0.0.0.0，允许局域网访问
    host: '0.0.0.0',
    // 代理配置
    proxy: {
      // 将所有以/api开头的请求代理到后端服务器
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      },
      // 将所有以/static开头的请求代理到后端服务器
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  // 生产环境配置
  outputDir: '../backend/static/frontend',
  // 资源路径
  publicPath: process.env.NODE_ENV === 'production' ? '/static/frontend/' : '/',
  // 生成的静态资源目录
  assetsDir: '',
  // 是否生成source map
  productionSourceMap: false
})
