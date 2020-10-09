<template>
    <b-container fluid class="my-4">
        <div v-if="noResults">
            <h6>
                This document does not have enough words from which to derive a
                topic distribution.
                <router-link :to="philoUrl"
                    >See full text of document</router-link
                >.
            </h6>
        </div>
        <div v-else>
            <h5 class="pl-4 pr-4" style="text-align: center">
                <citations
                    :docPair="mainDoc.metadata"
                    :philo-db="`${mainDoc.metadata.philo_db}`"
                    v-if="mainDoc"
                ></citations>
            </h5>

            <b-row class="mb-4 mt-4">
                <b-col cols="12" md="6" lg="7" xl="8">
                    <b-card no-body header="Top 10 Topics">
                        <div class="pl-2 pr-2">
                            <b-table
                                hover
                                :items="topicDistribution"
                                :fields="fields"
                                @row-clicked="goToTopic"
                            >
                                <template slot="[name]" slot-scope="data">
                                    <span class="frequency-parent"
                                        >Topic {{ data.value }}</span
                                    >
                                </template>
                                <template
                                    slot="[description]"
                                    slot-scope="data"
                                >
                                    <span class="frequency-parent">{{
                                        data.value
                                    }}</span>
                                </template>
                                <template slot="[frequency]" slot-scope="data">
                                    <span class="frequency-value pl-2"
                                        >{{ data.value }}%</span
                                    >
                                </template>
                            </b-table>
                        </div>
                    </b-card>
                </b-col>
                <b-col cols="12" md="6" lg="5" xl="4">
                    <b-card no-body style="height: 100%">
                        <template v-slot:header>
                            <h6
                                id="distinctive-words"
                                class="mb-0"
                                v-b-popover.hover.top="
                                    `Distinctiveness is computed using the Term Frequency - Inverse Document Frequency algorithm (TF-IDF)`
                                "
                            >
                                Most distinctive words
                                <span v-if="words.length == 50"
                                    >(up to 50 shown)</span
                                >
                            </h6>
                        </template>
                        <div id="word-cloud" class="card-text">
                            <div>
                                <span
                                    v-for="weightedWord in words"
                                    :key="weightedWord[2]"
                                >
                                    <word-link
                                        :target="weightedWord[2]"
                                        :metadata="mainDoc.metadata"
                                        :word="weightedWord[0]"
                                        :style="`display:inline-block; padding: 5px; cursor: pointer; font-size: ${
                                            1 + weightedWord[1]
                                        }rem; color: ${weightedWord[3]}`"
                                    ></word-link>
                                </span>
                            </div>
                        </div>
                    </b-card>
                </b-col>
            </b-row>
            <b-row class="mt-2">
                <div class="col-6">
                    <b-card
                        no-body
                        :header="`Top ${
                            topicSimDocs.slice(0, 20).length
                        } documents with most similar topic distribution`"
                    >
                        <b-list-group flush>
                            <b-list-group-item
                                v-for="(doc, topIndex) in topicSimDocs.slice(
                                    0,
                                    20
                                )"
                                :key="doc.doc_id"
                                class="list-group-item"
                                style="
                                    border-radius: 0px;
                                    border-width: 1px 0px;
                                "
                            >
                                <citations
                                    :docPair="doc.metadata"
                                    :philo-db="`${doc.metadata.philo_db}`"
                                    :index="`top-${topIndex}`"
                                ></citations>
                                <b-badge
                                    variant="secondary"
                                    pill
                                    class="float-right"
                                    >{{
                                        (doc.score * 100).toFixed(2)
                                    }}%</b-badge
                                >
                            </b-list-group-item>
                        </b-list-group>
                    </b-card>
                </div>
                <div class="col-6">
                    <b-card
                        no-body
                        :header="`Top ${vectorSimDocs.length} documents with most similar vocabulary`"
                    >
                        <b-list-group flush>
                            <b-list-group-item
                                v-for="(doc, vocIndex) in vectorSimDocs"
                                :key="doc.doc_id"
                                class="list-group-item"
                                style="
                                    border-radius: 0px;
                                    border-width: 1px 0px;
                                "
                            >
                                <citations
                                    :docPair="doc.metadata"
                                    :philo-db="`${doc.metadata.philo_db}`"
                                    :index="`voc-${vocIndex}`"
                                ></citations>
                                <b-badge
                                    variant="secondary"
                                    pill
                                    class="float-right"
                                    >{{
                                        (doc.score * 100).toFixed(0)
                                    }}%</b-badge
                                >
                            </b-list-group-item>
                        </b-list-group>
                    </b-card>
                </div>
            </b-row>
        </div>
    </b-container>
</template>
<script>
import Citations from "./Citations";
import WordLink from "./WordLink";

export default {
    name: "Document",
    components: {
        Citations,
        WordLink,
    },
    data() {
        return {
            noResults: true,
            mainDoc: null,

            text: "",
            words: [],
            fields: [
                { key: "name", label: "Topic", sortable: false },
                { key: "description", label: "Top 10 tokens", sortable: false },
                {
                    key: "frequency",
                    label: "Topic weight",
                    sortable: false,
                },
            ],
            vectorSimDocs: [],
            topicSimDocs: [],
            topicDistribution: [],
            philoUrl: `/navigate/${this.$route.params.philoDb}/${this.$route.params.doc}`,
            topicData: this.$topicModelData.topics_words,
        };
    },

    mounted() {
        this.fetchData();
    },
    watch: {
        // call again the method if the route changes
        $route: "loadNewData",
    },
    methods: {
        fetchData() {
            let philo_id = this.$route.params.doc.split("/").join(" ");
            this.text = "";

            this.$http
                .get(
                    `${this.$appConfig.topologic.api}/get_doc_data/${this.$appConfig.topologic.dbname}/${this.$route.params.philoDb}?philo_id=${philo_id}`
                )
                .then((response) => {
                    if (!response.data.metadata) {
                        this.noResults = true;
                    } else {
                        this.noResults = false;
                        this.words = response.data.words;
                        this.vectorSimDocs = response.data.vector_sim_docs;
                        this.topicSimDocs = response.data.topic_sim_docs;
                        this.mainDoc = {
                            metadata: response.data.metadata,
                            doc_id: "",
                            philo_id: response.data.metadata.philo_id,
                            philo_type: response.data.metadata.philo_type,
                        };
                        this.topicDistribution = this.buildTopicDistribution(
                            response.data.topic_distribution
                        );
                    }
                });
        },
        buildTopicDistribution(topicDistribution) {
            let total = topicDistribution.data.reduce((a, b) => a + b, 0);
            let data = topicDistribution.data.map((x) => (x / total) * 100);
            let modData = [];
            let modLabels = [];
            for (let label = 0; data.length > label; label += 1) {
                modData.push(data[label].toFixed(2));
                modLabels.push(label);
            }
            let zippedData = modLabels.map((e, i) => [e, modData[i]]);
            zippedData.sort(function (a, b) {
                return b[1] - a[1];
            });
            let sortedDistribution = [];
            let count = 0;
            for (let topic of zippedData) {
                sortedDistribution.push({
                    name: topic[0],
                    frequency: topic[1],
                    description: this.topicData[topic[0]].description,
                });
                count++;
                if (count == 10) {
                    break;
                }
            }
            return sortedDistribution;
        },
        loadNewData() {
            this.fetchData();
        },
        goToTopic(topic) {
            this.$router.push(`/topic/${topic.name}`);
        },
    },
};
</script>
<style scoped>
.popover {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
#word-cloud {
    display: flex;
    height: 100%;
    justify-content: center;
    align-items: center;
}
</style>
