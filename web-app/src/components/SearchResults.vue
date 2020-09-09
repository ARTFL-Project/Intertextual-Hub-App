<template>
    <div class="my-4">
        <b-card class="shadow-sm mb-4" style="position:relative">
            Input terms:
            <b v-if="binding == 'OR'">{{ searchTerms.split(" ").join(" OR ") }}</b>
            <b v-else>{{ searchTerms }}</b>
            <br />Bibliographic search criteria:
            <span v-if="author">
                <b>Author:</b>
                {{ author }}
            </span>
            <span v-if="title">
                <b>Title:</b>
                {{ title }}
            </span>
            <span v-if="date">
                <b>Date:</b>
                {{ date }}
            </span>
            <span v-if="!author && !title && !date">None</span>
            <div
                v-if="loading"
                class="text-center"
                style="position:absolute; left:0; right:0; z-index: 10"
            >
                <b-spinner
                    label="Loading..."
                    style="width: 5rem; height: 5rem; color: rgba(143, 57, 49, 0.8)"
                ></b-spinner>
            </div>
            <div class="mt-2" v-else>
                <span v-if="results">
                    Number of documents with {{ "this search term" | pluralize(searchTerms.split(" ").length) }}:
                    <b>{{ docCount }}</b>
                    <span v-if="results.length == 100">
                        <br />Displaying first 100 results:
                        &nbsp;use search filters to narrow search results
                    </span>
                </span>
                <span v-else>no results.</span>
                <!-- <br />Top 20 Author and Title Frequencies at bottom. -->
            </div>
        </b-card>
        <b-card
            class="position-relative mb-2 shadow-sm"
            v-for="(result, index) in results"
            :key="result.philo_id"
        >
            <span class="count">{{ index + 1 }}</span>
            <citations :docPair="result" :philo-db="`${result.philo_db}`"></citations>
            <span class="pl-2" v-if="!biblioQuery">(score: {{ result.score }})</span>
            <p class="mt-2 text" v-if="!biblioQuery" v-html="result.headline"></p>
            <div v-if="biblioQuery && result.sections.length > 0">
                <h6
                    class="mt-1"
                    style="color: rgb(143, 57, 49); cursor:pointer"
                    @click="showSections(index)"
                >See all chapters or sections</h6>
                <transition name="slide-fade">
                    <ul v-if="sectionsDisplay[index]">
                        <li v-for="section in result.sections" :key="section.philo_id">
                            <citations :docPair="section" :philo-db="`${result.philo_db}`"></citations>
                        </li>
                    </ul>
                </transition>
            </div>
        </b-card>
    </div>
</template>
<script>
import Citations from "./Citations";
import { EventBus } from "../main.js";

export default {
    name: "SearchResults",
    components: {
        Citations,
    },
    data() {
        return {
            searchTerms: this.$route.query.words,
            biblioQuery: false,
            title: this.$route.query.title,
            author: this.$route.query.author,

            results: null,
            docCount: null,
            sectionsDisplay: [],
            loading: false,
        };
    },
    computed: {
        date() {
            if (this.$route.query.date) {
                return this.$route.query.date.replace(/<=>/, "-");
            }
            return null;
        },
        binding() {
            return this.$route.query.binding;
        },
    },
    created() {
        if (!("words" in this.$route.query)) {
            this.biblioQuery = true;
        }
        this.fetchResults();
    },
    watch: {
        $route: "updateResults",
    },
    methods: {
        fetchResults() {
            EventBus.$emit("hideForms");
            this.results = null;
            this.loading = true;
            this.$http
                .get(
                    `https://anomander.uchicago.edu//intertextual-hub-api/search_texts?${this.paramsToUrlString(
                        this.$route.query
                    )}`
                )
                .then((response) => {
                    this.loading = false;
                    this.results = response.data.results;
                    this.sectionsDisplay = this.results.map(() => {
                        return false;
                    });
                    this.docCount = response.data.doc_count;
                });
        },
        updateResults() {
            this.searchTerms = this.$route.query.words;
            this.title = this.$route.query.title;
            this.author = this.$route.query.author;
            this.results = null;
            this.docCount = null;
            if (!("words" in this.$route.query)) {
                this.biblioQuery = true;
            } else {
                this.biblioQuery = false;
            }
            this.fetchResults();
        },
        showSections(index) {
            this.$set(this.sectionsDisplay, index, true);
        },
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
