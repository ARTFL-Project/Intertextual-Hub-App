import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import vueScrollTo from "vue-scrollto";
import VueApexCharts from "vue-apexcharts";
import appConfig from "./appConfig.json";

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
        deepEqual: function(x, y) {
            const ok = Object.keys,
                tx = typeof x,
                ty = typeof y;
            return x && y && tx === 'object' && tx === ty ? (
                ok(x).length === ok(y).length &&
                ok(x).every(key => this.deepEqual(x[key], y[key]))
            ) : (x === y);
        },
    },
});

Vue.directive('scroll', {
    inserted: function(el, binding) {
        el.scrollHandler = function(evt) {
            if (binding.value(evt, el)) {
                window.removeEventListener('scroll', el.scrollHandler)
            }
        }
        window.addEventListener('scroll', el.scrollHandler)
    },
    unbind: function(el) {
        window.removeEventListener("scroll", el.scrollHandler)
    }
})

Vue.filter('pluralize', (word, count) => {
    if (count == '1') {
        return word
    } else if (word == "this") {
        return `these ${count}`
    } else if (word.match(/this /)) {
        return `these ${word.split(" ")[1]} ${word.split(" ")[2]}s`
    }
    return `${word}s`
})

axios.get(
        `${appConfig.topologic.api}/get_config/${appConfig.topologic.dbname}?full_config=True`
    )
    .then((response) => {
        Vue.prototype.$topicModelData = response.data;

        new Vue({
            el: "#app",
            router,
            template: "<App/>",
            components: {
                App,
            },
            render: (h) => h(App),
        });
    });