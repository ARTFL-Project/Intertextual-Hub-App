<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand to="/">Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid>
            <b-tabs fill id="main-tabs" class="shadow-sm">
                <b-tab
                    :active="activeTab == 'intro'"
                    title="Intro to the HUB"
                    @click="selectModule('home')"
                >
                    <transition name="slide-fade">
                        <b-card style="border-top-width: 0" v-if="show">
                            <p style="text-align: justify; max-width:1000px">
                                The Intertextual Hub is a pilot project to develop a model that will allow scholars of 18th century France to bridge
                                the gap between distant and close reading when conducting research on large, heterogeneous digital text collections.
                            </p>
                            <!-- <h5>Top 5 most pre-rev author reused between 1789-1799</h5>
                            <ol>
                                <li>Jousse, Daniel 371252</li>
                                <li>La Mare, Nicolas de 85766</li>
                                <li>Chambon, M. 24645</li>
                                <li>Savary, Jacques 13418</li>
                                <li>Chardon, Daniel-Marc-Antoine 9490</li>
                            </ol>-->
                        </b-card>
                    </transition>
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
            } else if (report == "wordUse") {
                this.activeTab = "wordUse";
            }
            this.show = true;
        },
        showOptions() {
            this.show = true;
        },
    },
};
</script>

<style lang="scss">
@import "./assets/theme.scss";
@import "~bootstrap/scss/bootstrap.scss";
@import "~bootstrap-vue/src/index.scss";

::-webkit-scrollbar {
    -webkit-appearance: none;
    width: 7px;
}

::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: rgba(0, 0, 0, 0.5);
    box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}

a:not([href]) {
    color: #55acee;
    cursor: pointer;
}
a:not([href]):hover {
    color: $link-color;
    text-decoration: underline;
}
.link {
    cursor: pointer;
    color: $link-color;
    background-color: #fff;
    border-width: 0 !important;
    padding: 0;
    text-align: initial !important;
    vertical-align: initial;
    line-height: inherit;
}
.link:hover,
.link:focus,
.link:active {
    background-color: #fff !important;
    color: darken($link-color, 15%) !important;
    box-shadow: initial !important;
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
