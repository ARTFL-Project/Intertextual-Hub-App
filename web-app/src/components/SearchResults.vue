<template>
    <div class="mt-4">
        <b-card
            class="position-relative mb-2 shadow-sm"
            v-for="(result, index) in results"
            :key="result.philo_id"
        >
            <span class="count">{{index+1}}</span>
            <citations :docPair="result" :philo-db="`${result.philo_db}`"></citations>
            <span class="pl-2">(score: {{result.score}})</span>
            <p class="mt-2 text" v-html="result.headline"></p>
        </b-card>
    </div>
</template>
<script>
import Citations from "./Citations";

export default {
    name: "SearchResults",
    components: {
        Citations,
    },
    data() {
        return {
            results: null,
            doc_count: null,
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
                this.results = response.data.results;
                this.doc_count = response.data.doc_count;
                console.log(this.results);
            });
    },
};
</script>
<style scoped>
.count {
    position: absolute;
    top: 0;
    left: 0;
    padding: 0 0.25rem;
    border: #ddd solid 1px;
    border-width: 0 1px 1px 0;
    font-size: 0.8rem;
}
::v-deep .text b {
    color: indianred;
}
.text {
    line-height: 1.5rem;
}
</style>