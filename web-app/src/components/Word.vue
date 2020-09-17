<template>
    <div class="my-4">
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
                <b-row class="mt-4" no-gutters align-h="center" v-if="wordMovers && !singlePeriod">
                    <b-col cols="2" offset-md="4" align-self="center">
                        <h4 class="pl-3">Overall evolution:</h4>
                    </b-col>
                    <b-col cols="6">
                        <h5>
                            <a :id="`${wordMovers.max_up}-overall`">
                                <b>&nearr;</b>
                                {{ wordMovers.max_up }}
                            </a>
                            <word-link
                                :target="`${wordMovers.max_up}-overall`"
                                :word="wordMovers.max_up"
                                :extraLink="{link: `/search?words=${word}%20OR%20${wordMovers.max_up}`, text: `Find most relevant documents for <b>${word}</b> and <b>${wordMovers.max_up}</b>`}"
                            ></word-link>moved up the most
                        </h5>
                        <h5>
                            <a :id="`${wordMovers.max_down}-overall`">
                                <b>&searr;</b>
                                {{ wordMovers.max_down }}
                            </a>
                            <word-link
                                :target="`${wordMovers.max_down}-overall`"
                                :word="wordMovers.max_down"
                                :extraLink="{link: `/search?words=${word}%20OR%20${wordMovers.max_down}`, text: `Find most relevant documents for <b>${word}</b> and <b>${wordMovers.max_down}</b>`}"
                            ></word-link>moved down the most
                        </h5>
                    </b-col>
                </b-row>
                <div class="mt-4" v-else>
                    The term
                    <b>{{word}}</b>
                    only occurs in {{singlePeriod}}
                </div>
                <div class="mt-4" v-if="periodPairs">
                    <b-row
                        v-for="periodPair in periodPairs"
                        :key="`${periodPair.start.period}-${word}`"
                    >
                        <b-col cols="5">
                            <b-card class="mb-3 shadow-sm" no-body>
                                <template v-slot:header>
                                    <h5
                                        class="mb-0 text-center"
                                    >{{periodPair.start.period}}-{{parseInt(periodPair.start.period) + 24}}</h5>
                                </template>
                                <div class="card-text word-cloud">
                                    <div class="p-2">
                                        <span
                                            v-for="weightedWord in periodPair.start.words"
                                            :key="weightedWord.word"
                                        >
                                            <a
                                                :id="`${weightedWord.word}-${periodPair.start.period}`"
                                                :style="`font-size: ${1 + weightedWord.size}rem; color: ${weightedWord.color} !important`"
                                            >{{ weightedWord.word }}</a>
                                            <word-link
                                                :target="`${weightedWord.word}-${periodPair.start.period}`"
                                                :word="weightedWord.word"
                                                :extraLink="{link: makeCoocLink(word, weightedWord, periodPair), text: `Find most relevant documents for <b>${word}</b> and <b>${weightedWord.word}</b>`}"
                                            ></word-link>
                                        </span>
                                    </div>
                                </div>
                            </b-card>
                        </b-col>
                        <b-col cols="2" align-self="center">
                            <div>
                                <span style="font-size: 1.25rem">
                                    <a
                                        :id="`${periodPair.movers.max_up}-${periodPair.start.period}-movers`"
                                    >
                                        <b>&nearr;</b>
                                        {{ periodPair.movers.max_up }}
                                    </a>
                                    <word-link
                                        :target="`${periodPair.movers.max_up}-${periodPair.start.period}-movers`"
                                        :word="periodPair.movers.max_up"
                                        :extraLink="{link: `/search?words=${word}%20OR%20${periodPair.movers.max_up}`, text: `Find most relevant documents for <b>${word}</b> and <b>${periodPair.movers.max_up}</b>`}"
                                    ></word-link>
                                </span>
                                <br />
                                <span style="font-size: 1.25rem">
                                    <a
                                        :id="`${periodPair.movers.max_down}-${periodPair.start.period}-movers`"
                                    >
                                        <b>&searr;</b>
                                        {{ periodPair.movers.max_down }}
                                    </a>
                                    <word-link
                                        :target="`${periodPair.movers.max_down}-${periodPair.start.period}-movers`"
                                        :word="periodPair.movers.max_down"
                                        :extraLink="{link: `/search?words=${word}%20OR%20${periodPair.movers.max_down}`, text: `Find most relevant documents for <b>${word}</b> and <b>${periodPair.movers.max_down}</b>`}"
                                    ></word-link>
                                </span>
                            </div>
                        </b-col>
                        <b-col cols="5">
                            <b-card class="mb-3 shadow-sm" no-body>
                                <template v-slot:header>
                                    <h5
                                        class="mb-0 text-center"
                                    >{{periodPair.end.period}}-{{parseInt(periodPair.end.period) + 24}}</h5>
                                </template>
                                <div class="card-text word-cloud">
                                    <div class="p-2">
                                        <span
                                            v-for="weightedWord in periodPair.end.words"
                                            :key="weightedWord.word"
                                        >
                                            <a
                                                :id="`${weightedWord.word}-${periodPair.end.period}`"
                                                :style="`font-size: ${1 + weightedWord.size}rem; color: ${weightedWord.color} !important`"
                                            >{{ weightedWord.word }}</a>
                                            <word-link
                                                :target="`${weightedWord.word}-${periodPair.end.period}`"
                                                :word="weightedWord.word"
                                                :extraLink="{link: `/search?words=${word}%20OR%20${weightedWord.word}&date=${periodPair.end.period}<%3D>${(parseInt(periodPair.end.period) + 24)}`, text: `Find most relevant documents for <b>${word}</b> and <b>${weightedWord.word}</b>`}"
                                            ></word-link>
                                        </span>
                                    </div>
                                </div>
                            </b-card>
                        </b-col>
                    </b-row>
                </div>
            </b-tab>
        </b-tabs>
    </div>
</template>
<script>
import Citations from "./Citations";
import WordLink from "./WordLink";

export default {
    name: "Word",
    components: { Citations, WordLink },
    data() {
        return {
            localTopics: this.$topicModelData.topics_words,
            notFound: false,
            documents: [],
            topicDistribution: [],
            simWordsByTopics: [],
            simWordsByCooc: [],
            singlePeriod: null,
            wordMovers: null,
            fields: [
                { key: "name", label: "Topic", sortable: false },
                { key: "description", label: "Top 10 tokens", sortable: false },
                {
                    key: "frequency",
                    label: "Word weight in topic",
                    sortable: false,
                },
            ],
            periodPairs: [],
        };
    },
    computed: {
        word: function () {
            return this.$route.params.word;
        },
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
                    this.notFound = true;
                });
            this.$http
                .get(
                    `https://anomander.uchicago.edu/intertextual-hub-api/get_word_vectors/${this.$route.params.word}`
                )
                .then((response) => {
                    this.wordMovers = response.data.overall_movers;
                    let periods = Object.keys(response.data.evolution);
                    for (let i = 0; i < periods.length - 1; i += 1) {
                        this.periodPairs.push({
                            start: {
                                period: periods[i],
                                words: response.data.evolution[periods[i]],
                            },
                            end: {
                                period: periods[i + 1],
                                words: response.data.evolution[periods[i + 1]],
                            },
                            movers: response.data.movers[i],
                        });
                    }
                    if (this.periodPairs.length === 0) {
                        this.singlePeriod = `${periods[0]}-${
                            parseInt(periods[0]) + 25
                        }`;
                    }
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
            // this.word = this.$route.params.word;
            this.wordMovers = [];
            this.periodPairs = [];
            console.log(this.word);
            this.fetchData();
        },
        goToTopic(topic) {
            this.$router.push(`/topic/${topic.name}`);
        },
        makeCoocLink(word, weightedWord, periodPair) {
            return `/search?words=${word}%20OR%20${weightedWord.word}&date=${
                periodPair.start.period
            }<%3D>${parseInt(periodPair.start.period) + 24}`;
        },
    },
};
</script>

<style scoped>
.word-cloud {
    display: flex;
    height: 100%;
    justify-content: center;
    align-items: center;
}
.word-cloud a {
    display: inline-block;
    padding: 5px;
    cursor: pointer;
}
::v-deep .nav-tabs {
    border-bottom-width: 0;
}
::v-deep .nav-link {
    background-color: rgba(230, 230, 230, 0.6) !important;
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