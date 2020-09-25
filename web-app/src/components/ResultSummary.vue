<template>
    <div class="mt-4">
        <h5 v-if="results">
            Showing matches {{ currentStart + 1 }}-{{
                currentStart + results.length
            }}
            of {{ count }}
        </h5>
        <b-card
            class="mt-4 mb-4 shadow-sm"
            no-body
            v-for="(documentPair, resultsIndex) in results"
            :key="documentPair.pairid"
        >
            <span class="count">{{ resultsIndex + 1 + currentStart }}</span>
            <b-row class="px-3">
                <b-col sm="3" md="3" lg="2" align-self="center">
                    <h6 class="text-center">
                        {{ documentPair.passage_number }} common
                        {{ "passage" | pluralize(documentPair.passage_number) }}
                    </h6>
                </b-col>
                <b-col align-self="stretch" style="border-left: solid 1px #ddd">
                    <b-row>
                        <b-col
                            cols="12"
                            align-self="center"
                            class="p-3"
                            style="border-bottom: solid 1px #ddd"
                        >
                            <citations
                                :philo-db="documentPair.source_philo_db"
                                :docPair="documentPair"
                                direction="source"
                                :index="resultsIndex"
                            ></citations>
                        </b-col>
                        <b-col cols="12" align-self="center" class="p-3">
                            <citations
                                :philo-db="documentPair.target_philo_db"
                                :docPair="documentPair"
                                direction="target"
                                :index="resultsIndex"
                            ></citations>
                        </b-col>
                    </b-row>
                </b-col>
            </b-row>
            <b-row class="position-relative m-0">
                <b-col
                    class="position-absolute text-center"
                    style="top: -1.95rem"
                    sm="3"
                    md="3"
                    lg="2"
                >
                    <b-button
                        size="sm"
                        variant="info"
                        @click="
                            togglePassages(
                                documentPair,
                                documentPair.pairid,
                                resultsIndex
                            )
                        "
                        >{{
                            passageTogglerMessages[resultsIndex]
                                | pluralize(documentPair.passage_number)
                        }}</b-button
                    >
                </b-col>
            </b-row>

            <transition name="slide-fade">
                <div
                    class="pt-3 pb-2"
                    style="border-top: solid 1px #ddd"
                    v-if="passages[resultsIndex].length > 0"
                >
                    <div
                        v-for="(passage, passageIndex) in passages[
                            resultsIndex
                        ]"
                        :key="passage.passageid"
                    >
                        <hr
                            v-if="
                                passageIndex != 0 &&
                                passageIndex != passages[resultsIndex].length
                            "
                        />
                        <passage-pair
                            :passage="passage"
                            :source-philo-id="documentPair.source_philo_id"
                            :source-philo-db="documentPair.source_philo_db"
                            :target-philo-id="documentPair.target_philo_id"
                            :target-philo-db="documentPair.target_philo_db"
                            :passage-number="documentPair.passage_number"
                            :pairid="documentPair.pairid"
                        ></passage-pair>
                    </div>
                </div>
            </transition>
        </b-card>
        <div class="overflow-auto">
            <b-pagination-nav
                align="center"
                first-text="First"
                last-text="Last"
                limit="10"
                :link-gen="pages"
                :number-of-pages="pageCount"
                use-router
            ></b-pagination-nav>
        </div>
    </div>
</template>
<script>
import Citations from "./Citations";
import PassagePair from "./PassagePair";
import { EventBus } from "../main.js";

export default {
    name: "ResultSummary",
    components: { Citations, PassagePair },
    data() {
        return {
            results: null,
            passages: [],
            passageTogglerMessages: null,
            currentStart: 0,
            pageCount: 1,
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
            EventBus.$emit("hideForms");
            this.results = [];
            this.$http
                .get(
                    `${
                        this.$appConfig.apiServer
                    }/intertextual-hub-api/search_alignments?${this.paramsToUrlString(
                        this.$route.query
                    )}`
                )
                .then((response) => {
                    this.passageTogglerMessages = response.data.results.map(
                        () => "Show passage"
                    );
                    this.count = parseInt(response.data.count);
                    let pageCount = this.count / 50;
                    if (this.count % 50 != 0) {
                        pageCount += 1;
                    }
                    this.pageCount = pageCount;
                    this.results = response.data.results;
                    this.currentStart = parseInt(this.$route.query.start);
                    console.log(this.currentStart, this.$route.query);
                    this.passages = new Array(this.results.length).fill(
                        [],
                        0,
                        this.results.length
                    );
                });
        },
        togglePassages(documentPair, pairID, index) {
            if (this.passageTogglerMessages[index].startsWith("Show")) {
                this.$http
                    .get(
                        `${this.$appConfig.apiServer}/intertextual-hub-api/retrieve_passages/${pairID}`
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
                this.passageTogglerMessages[index] = "Hide passage";
            } else {
                this.passageTogglerMessages[index] = "Show passage";
                this.$set(this.passages, index, {});
            }
        },
        pages(value) {
            let currentQuery = this.copyObject(this.$route.query);
            currentQuery.start = ((value - 1) * 50).toString();
            return `/seq-pair/search?${this.paramsToUrlString(currentQuery)}`;
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
.count {
    position: absolute;
    top: 0;
    left: 0;
    padding: 0 0.25rem;
    border: #ddd solid 1px;
    border-width: 0 1px 1px 0;
    font-size: 0.8rem;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
    transform: translateY(-30px);
    opacity: 0;
}
</style>
