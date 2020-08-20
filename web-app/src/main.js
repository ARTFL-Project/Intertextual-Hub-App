import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import vueScrollTo from "vue-scrollto";
import VueApexCharts from "vue-apexcharts";
import appConfig from "./appConfig.json";
import hubConfig from "../../../config/intertextual_hub_config.json";

import {
    BootstrapVue,
    BootstrapVueIcons
} from "bootstrap-vue";
import axios from "axios";

Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.use(BootstrapVueIcons);
Vue.use(VueApexCharts);
Vue.component("apexchart", VueApexCharts);

Vue.prototype.$http = axios;
Vue.prototype.$scrollTo = vueScrollTo.scrollTo;
Vue.prototype.$appConfig = appConfig;
Vue.prototype.$hubConfig = hubConfig;
Vue.prototype.$report = "";
export const EventBus = new Vue(); // To pass messages between components

Vue.mixin({
    methods: {
        paramsToRoute: function(formValues, path) {
            let filteredFormValues = Object.keys(formValues)
                .filter((field) => formValues[field])
                .reduce((a, fieldName) => {
                    a[fieldName] = formValues[fieldName];
                    return a;
                }, {});
            let routeObject = {
                path: path,
                query: filteredFormValues,
            };
            return routeObject;
        },
        paramsToUrlString: function(params) {
            let queryParams = Object.keys(params).map(
                (param) => `${param}=${encodeURIComponent(params[param])}`
            );
            return queryParams.join("&");
        },
        copyObject: function(objectToCopy) {
            return JSON.parse(JSON.stringify(objectToCopy));
        },
    },
});

Vue.filter('pluralize', (word, count) => {
    if (count == '1') {
        return word
    }
    if (word == "this") {
        return `these ${count}`
    }
    return `${word}s`
})

new Vue({
    el: "#app",
    router,
    template: "<App/>",
    components: {
        App,
    },
    render: (h) => h(App),
});