<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand>Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid class="mt-4">
            <b-tabs>
                <b-tab title="Explore similar passages" active>
                    <similar-passage-form></similar-passage-form>
                </b-tab>
                <b-tab title="Explore Topics">
                    <topic-distributions></topic-distributions>
                </b-tab>
                <b-tab title="Search and Retrieval">
                    <b-card-text>Charlie's form</b-card-text>
                </b-tab>
            </b-tabs>
            <router-view></router-view>
        </b-container>
    </div>
</template>

<script>
import SimilarPassageForm from "./components/SimilarPassageForm.vue";
import TopicDistributions from "/var/www/html/topologic/combo/src/components/TopicDistributions.vue";

export default {
    name: "App",
    components: {
        SimilarPassageForm,
        TopicDistributions
    }
};
</script>

<style scoped>
</style>
