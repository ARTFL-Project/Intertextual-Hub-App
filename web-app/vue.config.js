const path = require("path");
const vueSrc = "./src";

module.exports = {
    // The dev server speaks plain HTTP. It used to read the host's live Let's Encrypt key
    // and certificate directly, for a hostname (anomander) this application has not run on
    // for years. Put a proxy in front of it if you need TLS while developing.
    devServer: {
        https: false,
        compress: true,
        disableHostCheck: true,
        headers: {
            "Access-Control-Allow-Origin": "*",
        },
    },
    assetsDir: "intertextual-hub/",
    configureWebpack: {
        resolve: {
            alias: {
                "@": path.resolve(__dirname, vueSrc)
            },
            extensions: ['.js', '.vue', '.json']
        }
    }
};