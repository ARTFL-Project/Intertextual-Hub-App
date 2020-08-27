<template>
    <b-container fluid class="mt-4">
        <b-tabs justified content-class="mt-3">
            <b-tab active>
                <template v-slot:title>
                    <span style="font-size: 1.2rem;">
                        Distribution of
                        <b>{{word}}</b> in the corpus
                    </span>
                </template>
                <div v-if="notFound" class="p-4">
                    <b>{{ word }}</b> not in vocabulary used for modeling. See
                    <router-link to="/view/word">here</router-link>&nbsp;for available tokens
                </div>
                <div class="row mt-4 p-2" v-if="!notFound">
                    <div class="col-7">
                        <b-row>
                            <b-col cols="12">
                                <b-card no-body class="shadow-sm">
                                    <template v-slot:header>
                                        <span class="mb-0">
                                            5 most important topics for
                                            <b>{{ word }}</b>
                                        </span>
                                    </template>
                                    <b-table
                                        hover
                                        :items="topicDistribution"
                                        :fields="fields"
                                        @row-clicked="goToTopic"
                                    >
                                        <template slot="[name]" slot-scope="data">
                                            <span class="frequency-parent">Topic {{ data.value }}</span>
                                        </template>
                                        <template slot="[description]" slot-scope="data">
                                            <span class="frequency-parent">{{ data.value }}</span>
                                        </template>
                                        <template slot="[frequency]" slot-scope="data">
                                            <span class="frequency-value pl-2">{{ data.value }}%</span>
                                        </template>
                                    </b-table>
                                </b-card>
                            </b-col>
                        </b-row>
                        <b-row class="mt-4">
                            <b-col cols="6">
                                <b-card
                                    no-body
                                    :header="`${simWordsByTopics.length} most associated words by topic distribution`"
                                >
                                    <b-list-group flush>
                                        <b-list-group-item
                                            v-for="word in simWordsByTopics"
                                            :key="word.word"
                                            class="list-group-item"
                                            style="border-radius: 0px; border-width: 1px 0px; font-size: 90%"
                                        >
                                            <a
                                                :id="`${word.word}-topics`"
                                                style="display:inline-block; cursor: pointer; "
                                            >{{ word.word }}</a>
                                            <word-link
                                                :target="`${word.word}-topics`"
                                                :word="word.word"
                                            ></word-link>
                                            <b-badge variant="secondary" pill class="float-right">
                                                {{
                                                word.weight.toFixed(4)
                                                }}
                                            </b-badge>
                                        </b-list-group-item>
                                    </b-list-group>
                                </b-card>
                            </b-col>
                            <b-col cols="6">
                                <b-card
                                    no-body
                                    :header="`${simWordsByCooc.length} most associated words by document co-occurrence`"
                                >
                                    <b-list-group flush>
                                        <b-list-group-item
                                            v-for="word in simWordsByCooc"
                                            :key="word.word"
                                            class="list-group-item"
                                            style="border-radius: 0px; border-width: 1px 0px; font-size: 90%"
                                        >
                                            <a
                                                :id="`${word.word}-docs`"
                                                style="display:inline-block; cursor: pointer; "
                                            >{{ word.word }}</a>
                                            <word-link
                                                :target="`${word.word}-docs`"
                                                :word="word.word"
                                            ></word-link>
                                            <b-badge variant="secondary" pill class="float-right">
                                                {{
                                                word.weight.toFixed(4)
                                                }}
                                            </b-badge>
                                        </b-list-group-item>
                                    </b-list-group>
                                </b-card>
                            </b-col>
                        </b-row>
                    </div>
                    <div class="col-5">
                        <b-card
                            no-body
                            class="shadow-sm"
                            :header="`Top ${documents.length} documents by relevance`"
                        >
                            <b-list-group flush>
                                <b-list-group-item
                                    v-for="doc in documents"
                                    :key="doc.doc_id"
                                    class="list-group-item"
                                    style="border-radius: 0px; border-width: 1px 0px; font-size: 90%"
                                >
                                    <citations
                                        :docPair="doc.metadata"
                                        :philo-db="`${doc.metadata.philo_db}`"
                                    ></citations>
                                    <b-badge
                                        variant="secondary"
                                        pill
                                        class="float-right"
                                    >{{ doc.score.toFixed(2) }}</b-badge>
                                </b-list-group-item>
                            </b-list-group>
                        </b-card>
                    </div>
                </div>
            </b-tab>
            <b-tab>
                <template v-slot:title>
                    <span style="font-size: 1.2rem;">
                        Evolution of words associated with
                        <b>{{word}}</b> over time
                    </span>
                </template>
                <b-row class="mt-4" v-if="wordEvolution">
                    <b-col cols="6" v-for="(decadeObj, decade) in wordEvolution" :key="decade">
                        <b-card class="mb-3 shadow-sm" no-body>
                            <template v-slot:header>
                                <h5 class="mb-0 text-center">{{decade}}-{{parseInt(decade) +10}}</h5>
                            </template>
                            <div
                                style="display: flex; height: 100%; justify-content: center; align-items: center;"
                                class="card-text"
                            >
                                <div class="p-3">
                                    <span
                                        v-for="weightedWord in decadeObj"
                                        :key="weightedWord.word"
                                    >
                                        <a
                                            :id="`${weightedWord.word}-${decade}`"
                                            :style="
                                        `display:inline-block; padding: 5px; cursor: pointer; font-size: ${1 +
                                            weightedWord.size}rem; color: ${
                                            weightedWord.color
                                        } !important`
                                    "
                                        >{{ weightedWord.word }}</a>
                                        <word-link
                                            :target="`${weightedWord.word}-${decade}`"
                                            :word="weightedWord.word"
                                        ></word-link>
                                    </span>
                                </div>
                            </div>
                        </b-card>
                    </b-col>
                </b-row>
            </b-tab>
        </b-tabs>
    </b-container>
</template>
<script>
import Citations from "./Citations";
import WordLink from "./WordLink";

export default {
    name: "Word",
    components: { Citations, WordLink },
    data() {
        return {
            word: "",
            localTopics: null,
            notFound: false,
            documents: [],
            topicDistribution: [],
            simWordsByTopics: [],
            simWordsByCooc: [],
            wordEvolution: null,
            fields: [
                { key: "name", label: "Topic", sortable: false },
                { key: "description", label: "Top 10 tokens", sortable: false },
                {
                    key: "frequency",
                    label: "Word weight in topic",
                    sortable: false,
                },
            ],
        };
    },
    created() {
        this.$http
            .get(
                `${this.$appConfig.topologic.api}/get_config/${this.$appConfig.topologic.dbname}?full_config=True`
            )
            .then((response) => {
                this.localTopics = response.data.topics_words;
            });
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
            this.$http
                .get(
                    `${this.$appConfig.topologic.api}/get_word_data/${this.$appConfig.topologic.dbname}/${this.$route.params.word}`
                )
                .then((response) => {
                    this.word = response.data.word;
                    if (response.data.documents.length > 0) {
                        this.documents = response.data.documents.slice(0, 10);
                        this.topicDistribution = this.build_topic_distribution(
                            response.data.topic_distribution
                        );
                        this.simWordsByTopics =
                            response.data.similar_words_by_topic;
                        this.simWordsByCooc =
                            response.data.similar_words_by_cooc;
                        this.notFound = false;
                    } else {
                        this.notFound = true;
                    }
                })
                .catch((error) => {
                    console.log(error);
                    this.word = this.$route.params.word;
                    this.notFound = true;
                });
            this.$http
                .get(
                    `https://anomander.uchicago.edu/intertextual-hub-api/get_word_vectors/${this.$route.params.word}`
                )
                .then((response) => {
                    this.wordEvolution = response.data;
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        build_topic_distribution(topicDistribution) {
            let joinedDistribution = [];
            for (let i = 0; i < this.localTopics.length; i += 1) {
                joinedDistribution.push({
                    name: i,
                    frequency: topicDistribution.data[i].toFixed(3),
                    description: this.localTopics[i].description,
                });
            }
            joinedDistribution.sort(function (a, b) {
                return b.frequency - a.frequency;
            });
            return joinedDistribution.slice(0, 5);
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
::v-deep .nav-tabs {
    border-bottom-width: 0;
}
::v-deep .nav-link {
    background-color: rgba(230, 230, 230, 0.4) !important;
    border-bottom: 1px solid #dee2e6;
    color: rgba(0, 0, 0, 0.6) !important;
    transition: all 250ms;
}

::v-deep .nav-link.active {
    background-color: rgba(230, 230, 230, 0.2) !important;
    border-bottom-color: transparent !important;
    color: rgb(0, 0, 0) !important;
}
</style>