import Vue from "vue";
import Router from "vue-router";
import ResultSummary from "../components/ResultSummary";
import TextNavigation from "../components/TextNavigation";
import TopicDistributions from "../components/TopicDistributions.vue";
import Topic from "../components/Topic.vue";
import Document from "../components/Document.vue";

Vue.use(Router);

export default new Router({
    mode: "history",
    base: "/",
    routes: [{
            path: "/",
            name: "home",
        },
        {
            path: "/navigate/:philoDb/:doc([\\d/]+)",
            name: "TextNavigation",
            components: {
                TextNavigation,
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
            path: "/topic-modeling",
            name: "topicModeling",
            components: {
                topicModeling: TopicDistributions,
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
            path: "/document/:doc",
            name: "Document",
            components: {
                Document
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