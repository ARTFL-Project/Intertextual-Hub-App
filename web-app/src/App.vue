<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
            <b-collapse id="nav-collapse" is-nav>
                <b-navbar-nav>
                    <b-nav-item href="https://intertextual-hub.org"
                        >Home</b-nav-item
                    >
                    <b-nav-item href="https://artfl-project.uchicago.edu"
                        >ARTFL Project</b-nav-item
                    >
                    <b-nav-item href="https://textual-optics-lab.uchicago.edu"
                        >Textual Optics Lab</b-nav-item
                    >
                    <b-nav-item href="https://neh.gov">NEH</b-nav-item>
                </b-navbar-nav>
            </b-collapse>
            <b-navbar-brand
                style="
                    font-weight: 700;
                    font-size: 1.6rem;
                    font-variant: small-caps;
                    position: absolute;
                    left: 50%;
                    transform: translateX(-50%);
                    line-height: 80%;
                "
                to="/"
                @click="goToHome()"
                >Intertextual Hub</b-navbar-brand
            >
        </b-navbar>
        <b-tabs fill no-fade v-model="tabIndex" id="main-tabs" class="shadow">
            <b-tab
                class="position-absolute shadow module-tab"
                title="Collections"
                @click="selectModule('home')"
            >
                <transition name="slide-fade">
                    <b-card style="border-top-width: 0" v-if="show">
                        <h5>Collections included in the Intertextual Hub:</h5>
                        <b-list-group style="width: fit-content">
                            <b-list-group-item
                                v-for="philoDb in philoDbs"
                                :key="philoDb.name"
                            >
                                <a :href="philoDb.url" target="_blank">{{
                                    philoDb.name
                                }}</a>
                                :
                                <span v-html="philoDb.description"></span>
                            </b-list-group-item>
                        </b-list-group>
                    </b-card>
                </transition>
                <div class="footer" v-if="routeName != 'TextNavigation'">
                    <b-container>
                        <p class="mb-0" style="font-variant: small-caps">
                            Sponsored by the
                        </p>
                        <a href="https://neh.gov" target="_blank">
                            <img
                                :src="`${publicPath}NEH-Preferred-Seal820.jpg`"
                                class="d-inline-block align-top"
                                style="width: 140px; height: 64px"
                                alt="NEH" /></a
                    ></b-container>
                </div>
            </b-tab>
            <b-tab
                class="position-absolute shadow module-tab"
                title="Search and Retrieval"
                @click="selectModule('search')"
            >
                <transition name="slide-fade">
                    <search-form v-if="show"></search-form>
                </transition>
            </b-tab>
            <b-tab
                class="position-absolute shadow module-tab"
                title="Explore text reuse"
                @click="selectModule('SeqPairResultsSummary')"
            >
                <transition name="slide-fade">
                    <similar-passage-form v-if="show"></similar-passage-form>
                </transition>
            </b-tab>
            <b-tab
                class="position-absolute shadow module-tab"
                title="Explore Topics"
                @click="selectModule('topicModeling')"
            >
                <transition name="slide-fade">
                    <topic-distributions v-if="show"></topic-distributions>
                </transition>
            </b-tab>

            <b-tab
                class="position-absolute shadow module-tab"
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
            >
                Click a tab to show navigation options
            </div>
        </transition>
        <b-container fluid style="margin-top: 3rem !important">
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
            report: this.$route.name,
            routeName: this.$route.name,
            show: true,
            word: "",
            philoDbs: this.$appConfig.philoDBs,
            tabIndex: 0,
            publicPath: process.env.BASE_URL,
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
        } else {
            this.show = true;
        }
    },
    methods: {
        selectModule(report, noShow) {
            let show;
            if (noShow === false) {
                show = false;
            } else if (!this.show) {
                show = true;
            } else if (this.show && report != this.report) {
                show = true;
            } else {
                show = false;
            }
            this.report = report;
            if (report == "SeqPairResultsSummary") {
                this.tabIndex = 2;
            } else if (report == "Topic" || report == "Document") {
                this.tabIndex = 3;
            } else if (report == "Search") {
                this.tabIndex = 1;
            } else if (report == "home") {
                this.tabIndex = 0;
            } else if (report == "wordUse") {
                this.tabIndex = 4;
            }
            this.show = show;
        },
        handleRouteChange(to) {
            this.routeName = to.name;
            if (to.name == "home") {
                this.selectModule("home", true);
            } else {
                this.selectModule(to.name, false);
            }
        },
        showOptions() {
            this.show = true;
        },
        goToHome() {
            this.$router.push({ name: "home" });
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
#nav-collapse .nav-item a {
    color: $link-color !important;
    font-size: 75%;
    font-variant: small-caps;
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
.module-tab {
    z-index: 50;
    width: 100%;
}
.footer {
    position: absolute;
    bottom: -8rem;
    width: 100%;
    text-align: center;
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
    transition: all 0.15s ease-out;
}
.fade-leave-active {
    transition: all 0.15s ease-out;
}
.fade-enter,
.fade-leave-to {
    opacity: 1;
}
</style>
