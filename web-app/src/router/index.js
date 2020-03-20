import Vue from 'vue'
import Router from 'vue-router'
import ResultSummary from '../components/ResultSummary'
import TextNavigation from "../components/TextNavigation"

Vue.use(Router)

export default new Router({
    mode: 'history',
    base: "/",
    routes: [{
            path: '/',
            name: 'home',
        },
        {
            path: '/navigate',
            name: "TextNavigation",
            component: TextNavigation
        },
        {
            path: '/search',
            name: 'ResultSummary',
            component: ResultSummary
        }
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition
        } else {
            return {
                x: 0,
                y: 0
            }
        }
    }
})