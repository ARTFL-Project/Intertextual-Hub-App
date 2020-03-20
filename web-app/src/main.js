import Vue from 'vue'
import App from './App.vue'
import router from "./router"
import appConfig from "./appConfig.json"

import {
    BootstrapVue,
    BootstrapVueIcons
} from "bootstrap-vue"
import "bootstrap/dist/css/bootstrap.css"
import "bootstrap-vue/dist/bootstrap-vue.css"
import axios from "axios"

Vue.config.productionTip = false

Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)
Vue.prototype.$http = axios
Vue.prototype.$appConfig = appConfig
export const EventBus = new Vue() // To pass messages between components

Vue.mixin({
    methods: {
        paramsToRoute: function(formValues) {
            let filteredFormValues = Object.keys(formValues)
                .filter(field => formValues[field])
                .reduce((a, fieldName) => {
                    a[fieldName] = formValues[fieldName];
                    return a;
                }, {});
            let routeObject = {
                path: `/search`,
                query: filteredFormValues
            }
            return routeObject
        },
        paramsToUrlString: function(params) {
            let queryParams = Object.keys(params).map(param => `${param}=${encodeURIComponent(params[param])}`)
            return queryParams.join('&')
        },
        copyObject: function(objectToCopy) {
            return JSON.parse(JSON.stringify(objectToCopy))
        },
    }
})

new Vue({
    el: "#app",
    router,
    template: "<App/>",
    components: {
        App
    },
    render: h => h(App)
})