import Vue from "vue";
import Router from "vue-router";
const ResultSummary = () =>
    import ("@/components/ResultSummary");
const TextNavigation = () =>
    import ("@/components/TextNavigation");
const Word = () =>
    import ("@/components/Word.vue");
const Topic = () =>
    import ("@/components/Topic.vue");
const Document = () =>
    import ("@/components/Document.vue");
import SearchResults from "@/components/SearchResults.vue"
import appConfig from "../../../config/appConfig.json";

Vue.use(Router);

export default new Router({
    mode: "history",
    base: appConfig.base,
    routes: [{
            path: "/",
            name: "home",
        },
        {
            path: "/navigate/:philoDb/:doc([\\d/]+)",
            name: "TextNavigation",
            components: {
                SeqPairResultsSummary: TextNavigation,
            },
        },
        {
            path: "/seq-pair/search",
            name: "SeqPairResultsSummary",
            components: {
                SeqPairResultsSummary: ResultSummary,
            },
        },
        {
            path: "/word/:word",
            name: "wordUse",
            components: {
                wordUse: Word,
            },
        },
        {
            path: "/topic/:topic",
            name: "Topic",
            components: {
                topicModeling: Topic,
            },
        },
        {
            path: "/document/:philoDb/:doc([\\d/]+)",
            name: "Document",
            components: {
                topicModeling: Document
            }
        },
        {
            path: "/search",
            name: "Search",
            components: {
                Search: SearchResults
            }
        }
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        } else {
            return {
                x: 0,
                y: 0,
            };
        }
    },
});