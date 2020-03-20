<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand>Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid class="mt-4">
            <search-form></search-form>
            <router-view></router-view>
        </b-container>
    </div>
</template>

<script>
import SearchForm from "./components/SearchForm.vue";

export default {
    name: "App",
    components: {
        SearchForm
    },
    data() {
        return {};
    }
};
</script>

<style scoped>
</style>
