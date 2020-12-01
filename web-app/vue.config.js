const fs = require("fs");
const path = require("path");
const vueSrc = "./src";

module.exports = {
    devServer: {
        https: true,
        key: fs.readFileSync(
            "/etc/letsencrypt/live/anomander.uchicago.edu/privkey.pem"
        ),
        cert: fs.readFileSync(
            "/etc/letsencrypt/live/anomander.uchicago.edu/fullchain.pem"
        ),
        compress: true,
        disableHostCheck: true,
        host: "anomander.uchicago.edu",
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