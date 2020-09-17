import Vue from "vue";
import Router from "vue-router";
import ResultSummary from "../components/ResultSummary";
import TextNavigation from "../components/TextNavigation";
import Word from "../components/Word.vue";
import Topic from "../components/Topic.vue";
import Document from "../components/Document.vue";
import SearchResults from "../components/SearchResults.vue"

Vue.use(Router);

export default new Router({
    mode: "history",
    base: "/intertextual-hub",
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