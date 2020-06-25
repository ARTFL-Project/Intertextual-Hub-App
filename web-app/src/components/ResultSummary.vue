<template>
    <div class="mt-4">
        <b-card
            class="p-3 mb-4 shadow-sm"
            no-body
            v-for="(documentPair, resultsIndex) in results"
            :key="resultsIndex"
        >
            {{ documentPair.passage_number}} common passages between:
            <br />
            <p style="line-height: 2rem">
                <citations
                    :philo-db="documentPair.source_philo_db"
                    :docPair="documentPair"
                    direction="source"
                ></citations>
                <b-button
                    class="ml-2"
                    pill
                    size="sm"
                    variant="outline-secondary"
                    @click="goToDocument(documentPair, 'source')"
                >See passage(s) in document</b-button>
                <br />
                <citations
                    :philo-db="documentPair.target_philo_db"
                    :docPair="documentPair"
                    direction="target"
                ></citations>
                <b-button
                    class="ml-2"
                    pill
                    size="sm"
                    variant="outline-secondary"
                    @click="goToDocument(documentPair, 'target')"
                >See passage(s) in document</b-button>
            </p>
            <div>
                <b-button @click="getPassages(documentPair.pairid, resultsIndex)">Show passages</b-button>
            </div>
            <!-- <div v-if="passages[resultsIndex].length > 0"></div> -->
        </b-card>
    </div>
</template>
<script>
import Citations from "./Citations";
export default {
    name: "ResultSummary",
    components: { Citations },
    data() {
        return {
            results: null,
            passages: []
        };
    },
    watch: {
        $route: "fetchResults"
    },
    created() {
        this.fetchResults();
    },
    methods: {
        goToDocument(documentPair, direction) {
            let link;
            if (direction == "source") {
                link = `/navigate/${
                    documentPair.source_philo_db
                }/${documentPair.source_philo_id.split(" ").join("/")}?pairid=${
                    documentPair.pairid
                }&direction=${direction}`;
            } else {
                link = `/navigate/${
                    documentPair.target_philo_db
                }/${documentPair.target_philo_id.split(" ").join("/")}?pairid=${
                    documentPair.pairid
                }&direction=${direction}`;
            }
            this.$router.push(link);
        },
        fetchResults() {
            this.$http
                .get(
                    `https://anomander.uchicago.edu//intertextual-hub-api/search?${this.paramsToUrlString(
                        this.$route.query
                    )}`
                )
                .then(response => {
                    this.results = response.data;
                    this.passages = new Array(this.results.length);
                });
        },
        getPassages(pairID, index) {
            this.$http
                .get(
                    `https://anomander.uchicago.edu//intertextual-hub-api/retrieve_passages/${pairID}`
                )
                .then(response => {
                    this.passages[index] = response.data;
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