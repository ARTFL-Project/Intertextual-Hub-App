<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand>Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid class="mt-4">
            <b-tabs>
                <b-tab :active="activeTab == 'intro'" title="Intro to the HUB">
                    <b-card class="mt-4 shadow-sm">This is what the Hub is all about...</b-card>
                </b-tab>
                <b-tab
                    :active="activeTab == 'textpair'"
                    title="Explore similar passages"
                    @click="selectModule('SeqPairResultsSummary')"
                >
                    <similar-passage-form></similar-passage-form>
                </b-tab>
                <b-tab
                    :active="activeTab == 'topics'"
                    title="Explore Topics"
                    @click="selectModule('topicModeling')"
                >
                    <div class="mt-2 p-2">
                        Click on any topic to explore its usage across the
                        corpus
                    </div>
                </b-tab>
                <b-tab
                    :active="activeTab == 'search'"
                    title="Search and Retrieval"
                    @click="selectModule('search')"
                >
                    <search-form></search-form>
                </b-tab>
            </b-tabs>
            <router-view name="SeqPairResultsSummary"></router-view>
            <router-view name="topicModeling"></router-view>
            <router-view name="Search"></router-view>
        </b-container>
    </div>
</template>

<script>
import SimilarPassageForm from "./components/SimilarPassageForm.vue";
import SearchForm from "./components/SearchForm";

export default {
    name: "App",
    components: {
        SimilarPassageForm,
        SearchForm,
    },
    data() {
        return {
            activeTab: "intro",
            report: this.$route.name,
        };
    },
    created() {
        console.log(this.$route.name);
        this.selectModule(this.report);
    },
    methods: {
        selectModule(report) {
            this.report = report;
            if (report == "SeqPairResultsSummary") {
                this.activeTab = "textpair";
            } else if (report == "topicModeling") {
                this.activeTab = "topics";
                this.$router.push("/topic-modeling");
            } else if (report == "Search") {
                this.activeTab = "search";
            } else if (report == "intro") {
                this.activeTab = "intro";
            }
        },
    },
};
</script>

<style scoped>
</style>
