<template>
    <div>Hi there</div>
</template>
<script>
export default {
    name: "SearchResults",
    data() {
        return {
            results: null,
        };
    },
    created() {
        this.$http
            .get(
                `https://anomander.uchicago.edu//intertextual-hub-api/search_texts?${this.paramsToUrlString(
                    this.$route.query
                )}`
            )
            .then((response) => {
                this.results = response.data;
                console.log(this.results);
            });
    },
};
</script>