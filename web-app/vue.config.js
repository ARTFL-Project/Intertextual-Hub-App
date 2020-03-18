module.exports = {
    devServer: {
        compress: true,
        disableHostCheck: true,
        host: "anomander.uchicago.edu",
        headers: {
            'Access-Control-Allow-Origin': '*'
        }
    },
    chainWebpack: config => {
        config.externals({
            Vue: 'vue'
        })
    },
    runtimeCompiler: true,
}