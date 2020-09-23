<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav align="center" style="width: 100%">
                <b-navbar-brand to="/">Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>

        <b-tabs fill no-fade id="main-tabs" class="shadow-sm">
            <b-tab
                class="position-absolute shadow"
                style="z-index:10; width: 100%"
                :active="activeTab == 'intro'"
                title="Collections"
                @click="selectModule('home')"
            >
                <transition name="slide-fade">
                    <b-card style="border-top-width: 0" v-if="show">
                        <h5>Here are the collections included in the Intertextual Hub:</h5>
                        <b-list-group style="width: fit-content;">
                            <b-list-group-item v-for="philoDb in philoDbs" :key="philoDb.name">
                                <a :href="philoDb.url" target="_blank">{{philoDb.name}}</a>
                                :
                                <span v-html="philoDb.description"></span>
                            </b-list-group-item>
                        </b-list-group>
                    </b-card>
                </transition>
            </b-tab>
            <b-tab
                class="position-absolute shadow"
                style="z-index:10"
                :active="activeTab == 'search'"
                title="Search and Retrieval"
                @click="selectModule('search')"
            >
                <transition name="slide-fade">
                    <search-form v-if="show"></search-form>
                </transition>
            </b-tab>
            <b-tab
                class="position-absolute shadow"
                style="z-index:10; width: 100%"
                :active="activeTab == 'textpair'"
                title="Explore text reuse"
                @click="selectModule('SeqPairResultsSummary')"
            >
                <transition name="slide-fade">
                    <similar-passage-form v-if="show"></similar-passage-form>
                </transition>
            </b-tab>
            <b-tab
                class="position-absolute shadow"
                style="z-index:10; width: 100%; background-color: #fff"
                :active="activeTab == 'topics'"
                title="Explore Topics"
                @click="selectModule('topicModeling')"
            >
                <transition name="slide-fade">
                    <topic-distributions v-if="show"></topic-distributions>
                </transition>
            </b-tab>

            <b-tab
                class="position-absolute shadow"
                style="z-index:10; width: 100%"
                :active="activeTab == 'wordUse'"
                title="Explore word usage"
                @click="selectModule('wordUse')"
            >
                <transition name="slide-fade">
                    <word-search v-if="show"></word-search>
                </transition>
            </b-tab>
        </b-tabs>
        <transition name="fade">
            <div
                id="show"
                class="p-2 position-absolute"
                v-if="!show"
                @click="showOptions()"
            >Click tab to show navigation options</div>
        </transition>
        <b-container fluid style="margin-top: 3rem !important;">
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
            philoDbs: this.$appConfig.philoDBs,
        };
    },
    watch: {
        $route: "handleRouteChange",
    },
    created() {
        this.selectModule(this.report);
        EventBus.$on("hideForms", () => {
            this.show = false;
        });
        if (this.$route.path != "/") {
            this.show = false;
        }
    },
    methods: {
        selectModule(report) {
            let show;
            if (!this.show) {
                show = true;
            } else if (this.show && report != this.report) {
                show = true;
            } else {
                show = false;
            }
            this.report = report;
            if (report == "SeqPairResultsSummary") {
                this.activeTab = "textpair";
            } else if (report == "Topic" || report == "Document") {
                this.activeTab = "topics";
            } else if (report == "Search") {
                this.activeTab = "search";
            } else if (report == "intro") {
                this.activeTab = "intro";
            } else if (report == "wordUse") {
                this.activeTab = "wordUse";
            }
            this.show = show;
        },
        handleRouteChange(to) {
            this.selectModule(to.name);
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
.navbar-brand {
    color: $link-color !important;
    font-variant: small-caps;
    font-weight: 700;
    font-size: 1.8rem;
    padding: 0;
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
    font-size: 0.9rem;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter,
.slide-fade-leave-to {
    transform: translateY(-30px);
    opacity: 0;
}
.fade-enter-active {
    // animation-delay: 2s;
    transition: all 0.15s ease-out;
}
.fade-leave-active {
    // animation-delay: 2s;
    transition: all 0.15s ease-out;
}
.fade-enter,
.fade-leave-to {
    opacity: 1;
}
</style>
