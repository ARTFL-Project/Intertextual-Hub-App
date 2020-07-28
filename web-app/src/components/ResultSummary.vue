<template>
    <div class="mt-4">
        <h5 v-if="results">Showing results 1-{{ results.length }}</h5>
        <b-card
            class="p-3 mb-4 shadow-sm"
            no-body
            v-for="(documentPair, resultsIndex) in results"
            :key="documentPair.pairid"
        >
            {{ documentPair.passage_number }} common passages between:
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
                    >See passage(s) in document</b-button
                >
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
                    >See passage(s) in document</b-button
                >
            </p>
            <div>
                <b-button
                    @click="
                        togglePassages(
                            documentPair,
                            documentPair.pairid,
                            resultsIndex
                        )
                    "
                    >{{ passageTogglerMessages[resultsIndex] }}</b-button
                >
            </div>
            <div
                v-for="(passage, passageIndex) in passages[resultsIndex]"
                :key="passage.passageid"
            >
                <hr
                    v-if="
                        passageIndex != 0 &&
                            passageIndex != passages[resultsIndex].length
                    "
                />
                <passage-pair :passage="passage"></passage-pair>
            </div>
        </b-card>
    </div>
</template>
<script>
import Citations from "./Citations";
import PassagePair from "./PassagePair";
export default {
    name: "ResultSummary",
    components: { Citations, PassagePair },
    data() {
        return {
            results: null,
            passages: [],
            passageTogglerMessages: null,
        };
    },
    watch: {
        $route: "fetchResults",
    },
    created() {
        this.fetchResults();
    },
    methods: {
        goToDocument(documentPair, direction) {
            let link;
            if (direction == "source") {
                link = this.paramsToRoute(
                    {
                        pairid: documentPair.pairid,
                        direction: direction,
                    },
                    `/navigate/${
                        documentPair.source_philo_db
                    }/${documentPair.source_philo_id.split(" ").join("/")}`
                );
            } else {
                link = this.paramsToRoute(
                    {
                        pairid: documentPair.pairid,
                        direction: direction,
                    },
                    `/navigate/${
                        documentPair.target_philo_db
                    }/${documentPair.target_philo_id.split(" ").join("/")}`
                );
            }
            this.$router.push(link);
        },
        fetchResults() {
            this.$http
                .get(
                    `https://anomander.uchicago.edu//intertextual-hub-api/search_alignments?${this.paramsToUrlString(
                        this.$route.query
                    )}`
                )
                .then((response) => {
                    this.passageTogglerMessages = response.data.map(
                        () => "Show passages"
                    );
                    this.results = response.data;
                    this.passages = new Array(this.results.length).fill(
                        [],
                        0,
                        this.results.length
                    );
                });
        },
        togglePassages(documentPair, pairID, index) {
            if (this.passageTogglerMessages[index] == "Show passages") {
                this.$http
                    .get(
                        `https://anomander.uchicago.edu//intertextual-hub-api/retrieve_passages/${pairID}`
                    )
                    .then((response) => {
                        response.data[0].metadata = {
                            source_author: documentPair.source_author,
                            source_title: documentPair.source_title,
                            source_head: documentPair.source_head,
                            source_date: documentPair.source_date,
                            target_author: documentPair.target_author,
                            target_title: documentPair.target_title,
                            target_head: documentPair.target_head,
                            target_date: documentPair.target_date,
                        };
                        this.$set(this.passages, index, response.data);
                    });
                this.passageTogglerMessages[index] = "Hide passages";
            } else {
                this.passageTogglerMessages[index] = "Show passages";
                this.$set(this.passages, index, {});
            }
        },
    },
};
</script>
<style scoped>
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
