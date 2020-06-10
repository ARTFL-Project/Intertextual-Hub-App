<template>
    <div class="mt-4">
        <b-card
            class="p-3 mb-4 shadow-sm"
            no-body
            v-for="(documentPair, resultIndex) in results"
            :key="resultIndex"
        >
            {{ documentPair.alignment_count}} common passages between:
            <br />
            <p>
                <span v-if="documentPair.source_author">
                    {{ documentPair.source_author }}
                    <span class="separator">&#9679;</span>
                </span>
                <i>{{ documentPair.source_title }}</i>
                <span class="separator">&#9679;</span>
                <span v-if="documentPair.source_year">{{ documentPair.source_year }}</span>
                &nbsp;
                <a
                    :href="`/navigate?source_philo_id=${documentPair.source_philo_id}&target_philo_id=${documentPair.target_philo_id}&direction=source`"
                >See passages in document</a>
                <br />
                <span v-if="documentPair.target_author">
                    {{ documentPair.target_author }}
                    <span class="separator">&#9679;</span>
                </span>
                <i>{{ documentPair.target_title }}</i>
                <span class="separator">&#9679;</span>
                <span v-if="documentPair.target_year">{{ documentPair.target_year }}</span>
                &nbsp;
                <a
                    :href="`/navigate?source_philo_id=${documentPair.source_philo_id}&target_philo_id=${documentPair.target_philo_id}&direction=target`"
                >See passages in document</a>
            </p>
        </b-card>
    </div>
</template>
<script>
export default {
    name: "ResultSummary",
    data() {
        return {
            results: null
        };
    },
    watch: {
        $route: "fetchResults"
    },
    created() {
        this.fetchResults();
    },
    methods: {
        fetchResults() {
            this.$http
                .get(
                    `https://anomander.uchicago.edu//intertextual-hub-api/search?${this.paramsToUrlString(
                        this.$route.query
                    )}`
                )
                .then(response => {
                    this.results = response.data;
                });
        }
    }
};
</script>
<style  scoped>
.separator {
    display: inline-block;
    padding: 0 0.5rem;
    font-size: 0.5rem;
    vertical-align: middle;
}
.source-passage,
.target-passage {
    color: dodgerblue;
}
</style>