import Vue from 'vue'
import App from './App.vue'
import router from "./router"

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
export const EventBus = new Vue() // To pass messages between components


new Vue({
    el: "#app",
    router,
    template: "<App/>",
    components: {
        App
    },
    render: h => h(App)
})