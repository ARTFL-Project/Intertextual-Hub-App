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
            </b-input-group>
        </b-form>
    </b-card>
</template>
<script>
export default {
    name: "WordSearch",
    data() {
        return {
            word: "",
        };
    },
    mounted() {
        if ("word" in this.$route.query) {
            this.word = this.$route.query.word;
        }
    },
    methods: {
        search() {
            this.$router.push(`/word/${this.word}`);
        },
    },
};
</script>