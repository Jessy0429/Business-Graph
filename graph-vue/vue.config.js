module.exports = {
    lintOnSave: false,
    devServer: {
        host: '0.0.0.0',
        port: 8080,
        // proxy: {
        //     '/api': {
        //         target: 'http://127.0.0.1:5000/api',
        //         changeOrigin: true,
        //         pathRewrite: {
        //             '^/api': ''
        //         }
        //     }
        // }
    },
};