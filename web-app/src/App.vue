<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand to="/">Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid class="mt-4">
            <b-tabs>
                <b-tab
                    :active="activeTab == 'intro'"
                    title="Intro to the HUB"
                    @click="selectModule('home')"
                >
                    <transition name="slide-fade">
                        <b-card
                            class="shadow-sm"
                            style="border-top-width: 0"
                            v-if="show"
                        >This is what the Hub is all about...</b-card>
                    </transition>
                </b-tab>
                <b-tab
                    :active="activeTab == 'textpair'"
                    title="Explore text reuse"
                    @click="selectModule('SeqPairResultsSummary')"
                >
                    <transition name="slide-fade">
                        <similar-passage-form v-if="show"></similar-passage-form>
                    </transition>
                </b-tab>
                <b-tab
                    :active="activeTab == 'topics'"
                    title="Explore Topics"
                    @click="selectModule('topicModeling')"
                >
                    <div class="mt-2 p-2" v-if="show">
                        Click on any topic to explore its usage across the
                        corpus
                    </div>
                    <topic-distributions v-if="show"></topic-distributions>
                </b-tab>
                <b-tab
                    :active="activeTab == 'search'"
                    title="Search and Retrieval"
                    @click="selectModule('search')"
                >
                    <transition name="slide-fade">
                        <search-form v-if="show"></search-form>
                    </transition>
                </b-tab>
                <b-tab
                    :active="activeTab == 'wordUse'"
                    title="Explore word usage"
                    @click="selectModule('wordUse')"
                >
                    <transition name="slide-fade">
                        <word-search></word-search>
                    </transition>
                </b-tab>
            </b-tabs>
            <transition name="fade">
                <div
                    id="show"
                    class="px-3"
                    v-if="!show"
                    @click="showOptions()"
                >Click tab to show navigation options</div>
            </transition>

            <router-view name="SeqPairResultsSummary"></router-view>
            <router-view name="topicModeling"></router-view>
            <router-view name="Search"></router-view>
            <router-view name="wordUse"></router-view>
        </b-container>
    </div>
</template>

<script>
import SimilarPassageForm from "./components/SimilarPassageForm.vue";
import SearchForm from "./components/SearchForm";
import TopicDistributions from "./components/TopicDistributions.vue";
import WordSearch from "./components/WordSearch.vue";
import { EventBus } from "./main.js";

export default {
    name: "App",
    components: {
        SimilarPassageForm,
        SearchForm,
        TopicDistributions,
        WordSearch,
    },
    data() {
        return {
            activeTab: "intro",
            report: this.$route.name,
            show: true,
            word: "",
        };
    },
    created() {
        this.selectModule(this.report);
        EventBus.$on("hideForms", () => {
            this.show = false;
            // this.activeTab = "";
        });
    },
    methods: {
        selectModule(report) {
            this.report = report;
            if (report == "SeqPairResultsSummary") {
                this.activeTab = "textpair";
            } else if (report == "topicModeling") {
                this.activeTab = "topics";
            } else if (report == "search") {
                this.activeTab = "search";
            } else if (report == "intro") {
                this.activeTab = "intro";
            }
            this.show = true;
        },
        showOptions() {
            this.show = true;
        },
    },
};
</script>

<style>
::-webkit-scrollbar {
    -webkit-appearance: none;
    width: 7px;
}

::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: rgba(0, 0, 0, 0.5);
    box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}
#show {
    cursor: pointer;
    color: #111;
    font-weight: 600;
    font-size: 0.85rem;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
    transform: translateY(-30px);
    opacity: 0;
}
.fade-enter-active {
    transition: all 0.3s ease-out;
}
.fade-leave-active {
    transition: all 0.3s ease-out;
}
.fade-enter, .fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
    opacity: 1;
}
</style>
