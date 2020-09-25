<template>
    <b-card style="border-top-width: 0">
        <b-form @submit.stop.prevent="search">
            <b-input-group prepend="Word" id="word" class="pb-1">
                <b-form-input
                    v-model.lazy="word"
                    placeholder="e.g. patrie"
                    style="max-width: 300px"
                ></b-form-input>
                <b-input-group-append>
                    <b-button variant="primary" type="submit">Search</b-button>
                </b-input-group-append>
                <span class="d-inline-block pl-2 mt-2"
                    >Note that words are unaccented automatically.</span
                >
            </b-input-group>
        </b-form>
    </b-card>
</template>
<script>
export default {
    name: "WordSearch",
    data() {
        return {
            word: this.$route.params.word || "",
        };
    },
    mounted() {
        if ("word" in this.$route.query) {
            this.word = this.$route.query.word;
        }
    },
    watch: {
        // call again the method if the route changes
        $route: function () {
            this.word = this.$route.params.word || "";
        },
    },
    methods: {
        search() {
            this.$router.push(`/word/${this.word}`);
        },
    },
};
</script>