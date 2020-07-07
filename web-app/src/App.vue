<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand>Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid class="mt-4">
            <b-tabs>
                <b-tab
                    :active="activeTab.SeqPairResultsSummary"
                    title="Explore similar passages"
                    @click="selectModule('SeqPairResultsSummary')"
                >
                    <similar-passage-form></similar-passage-form>
                </b-tab>
                <b-tab
                    :active="activeTab.topicModeling"
                    title="Explore Topics"
                    @click="selectModule('topicModeling')"
                >
                    <div class="mt-2 p-2">
                        Click on any topic to explore its usage across the
                        corpus
                    </div>
                </b-tab>
                <b-tab
                    :active="activeTab.search"
                    title="Search and Retrieval"
                    @click="selectModule('search')"
                >
                    <iframe
                        class="mt-2"
                        src="https://anomander.uchicago.edu/intertextual_hub/sqlite/multipledb.sqlite.html"
                        v-if="report == 'search'"
                    ></iframe>
                </b-tab>
            </b-tabs>
            <router-view name="SeqPairResultsSummary"></router-view>
            <router-view name="topicModeling"></router-view>
            <router-view name="TextNavigation"></router-view>
            <router-view name="document"></router-view>
        </b-container>
    </div>
</template>

<script>
import SimilarPassageForm from "./components/SimilarPassageForm.vue";

export default {
    name: "App",
    components: {
        SimilarPassageForm
    },
    data() {
        return {
            activeTab: {
                SeqPairResultsSummary: false,
                topicModeling: false,
                search: false
            },
            report: this.$route.name
        };
    },
    created() {
        for (let key in this.activeTab) {
            if (key == this.report) {
                this.activeTab[key] = true;
            } else {
                this.activeTab[key] = false;
            }
        }
    },
    methods: {
        selectModule(report) {
            this.report = report;
            if (report == "SeqPairResultsSummary") {
                this.$router.push("/");
            }
            if (report == "topicModeling") {
                this.$router.push("/topic-modeling");
            }
        }
    }
};
</script>

<style scoped>
iframe {
    width: 100%;
    height: 4096px;
}
iframe > html > body > nav {
    display: none;
}
</style>
