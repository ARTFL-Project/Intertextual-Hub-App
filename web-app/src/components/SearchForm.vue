<template>
    <b-card class="position-relative border-top-0">
        <b-row>
            <b-col sm="12" lg="8" xl="7">
                <b-form @submit.stop.prevent="search" @reset="clearForm">
                    <b-input-group prepend="Words" id="words" class="pb-1">
                        <b-form-input
                            v-model.lazy="formValues.words"
                            placeholder="e.g. conspirateurs aristocrates ennemis royalistes"
                        ></b-form-input>
                        <template v-slot:append>
                            <b-dropdown text="Select topic" right offset="10" variant="outline-secondary">
                                <b-dropdown-item
                                    v-for="topic in topics"
                                    :key="topic.name"
                                    @click="selectTopic(topic.description)"
                                >
                                    <b>Topic {{ topic.name }}:</b>
                                    {{ topic.description }}
                                </b-dropdown-item>
                            </b-dropdown>
                        </template>
                    </b-input-group>
                    <b-form-checkbox
                        v-model="formValues.stemmed"
                        name="stemmed"
                        value="yes"
                        checked-value
                        class="d-inline-block mb-3 mr-3"
                        >stem words</b-form-checkbox
                    >
                    <b-form-checkbox
                        v-model="formValues.binding"
                        name="binding"
                        value="OR"
                        unchecked-value
                        class="d-inline-block mb-3"
                        >OR search</b-form-checkbox
                    >
                    <b-button
                        size="sm"
                        variant="outline-primary"
                        class="d-inline-block ml-3 mb-3"
                        style="vertical-align: baseline"
                        @click="addAssociatedWords()"
                        >add 10 most associated words</b-button
                    >
                    <b-alert
                        :show="dismissCountDown"
                        @dismissed="dismissCountDown = 0"
                        @dismiss-count-down="countDownChanged"
                        variant="danger"
                        dismissible
                        fade
                    >
                        The term
                        <b>{{ formValues.words }}</b> is not present in the associated words index
                    </b-alert>
                    <b-input-group
                        :prepend="field.label"
                        class="pb-3"
                        v-for="field in metadataFields"
                        :key="field.label"
                    >
                        <b-form-input
                            v-model="formValues[field.value]"
                            :placeholder="`e.g. ${field.example}`"
                        ></b-form-input>
                    </b-input-group>
                    <b-input-group class="pb-3">
                        <template v-slot:prepend>
                            <b-input-group-text>Date</b-input-group-text>
                            <b-dropdown :text="dateType" variant="outline-secondary">
                                <b-dropdown-item @click="dropSelect('exact')">exact</b-dropdown-item>
                                <b-dropdown-item @click="dropSelect('range')">range</b-dropdown-item>
                            </b-dropdown>
                        </template>
                        <b-form-input
                            v-model="formValues['date']"
                            v-if="dateType == 'exact'"
                            placeholder="e.g. 1789"
                        ></b-form-input>
                        <b-input-group
                            prepend="from"
                            v-if="dateType == 'range'"
                            class="d-inline-flex ml-3"
                            style="width: auto"
                        >
                            <b-form-input
                                v-model="dateRange.from"
                                placeholder="e.g. 1770"
                                class="d-inline-flex"
                            ></b-form-input>
                        </b-input-group>
                        <b-input-group
                            prepend="to"
                            v-if="dateType == 'range'"
                            class="d-inline-flex ml-3"
                            style="width: auto"
                        >
                            <b-form-input
                                v-model="dateRange.to"
                                placeholder="e.g. 1799"
                                class="d-inline-flex"
                            ></b-form-input>
                        </b-input-group>
                    </b-input-group>
                    <b-input-group prepend="Collections" class="mb-3">
                        <b-form-select v-model="collectionSelected" :options="collections"></b-form-select>
                    </b-input-group>
                    <b-input-group prepend="Period" class="mb-3">
                        <b-form-select v-model="periodSelected" :options="periods"></b-form-select>
                    </b-input-group>

                    <b-form-group>
                        <b-input-group class="d-inline" prepend="Max results displayed"></b-input-group>
                        <b-form-radio-group
                            v-model="formValues.limit"
                            :options="[100, 250, 500]"
                            buttons
                            button-variant="outline-secondary"
                            name="radios-btn-default"
                        ></b-form-radio-group>
                    </b-form-group>
                    <b-button-group class="d-block mt-4">
                        <b-button variant="primary" type="submit">Search</b-button>
                        <b-button type="reset" variant="outline-primary">Reset</b-button>
                    </b-button-group>
                </b-form>
            </b-col>
            <b-col class="d-xs-none d-md-none d-lg-block">
                <p>Term queries run from this form return a list of documents ranked by revelance.</p>
                <p>
                    Queries can be executed just with search terms or can be delimited using bibliographic criteria.
                    Simple bibliographic queries work, as well. Author and Title fields accept boolean ORs.
                </p>
                <p>
                    Metadata permitting, queries can be delimited by date down to the day. The format for dates is
                    "YYYY-MM-DD", "YYYY-MM", or just "YYYY". End dates support date-range searching.
                </p>
            </b-col>
        </b-row>
        <b-button variant="outline-primary" style="position: absolute; right: 1.25rem; bottom: 1rem" @click="hideForm()"
            >Close</b-button
        >
    </b-card>
</template>
<script>
import { EventBus } from "../main.js";

export default {
    name: "SearchForm",
    data() {
        return {
            metadataFields: [
                {
                    label: "Author",
                    value: "author",
                    example: "Rousseau, Jean-Jacques",
                },
                {
                    label: "Title",
                    value: "title",
                    example: "Du contrat social",
                },
            ],
            dateType: "exact",
            dateRange: {
                to: null,
                from: null,
            },
            collections: [
                { text: "All collections", value: null },
                ...Object.keys(this.$appConfig.philoDBs).map((i) => {
                    return { value: i, text: this.$appConfig.philoDBs[i].name };
                }),
            ],
            collectionSelected: null,
            periods: [{ text: "All periods", value: null }, ...this.$appConfig.periods],
            periodSelected: null,
            formValues: { limit: 100, stemmed: "yes" },
            topics: this.$topicModelData.topics_words,
            showError: false,
            dismissCountDown: 0,
        };
    },
    created() {
        if (Object.keys(this.$route.query).length > 0) {
            this.formValues = this.copyObject(this.$route.query);
            if ("date" in this.$route.query && this.$route.query["date"].match("<=>")) {
                this.dateType = "range";
                let splitDates = this.$route.query["date"].split("<=>");
                this.dateRange.from = splitDates[0];
                this.dateRange.to = splitDates[1];
            }
            if ("collections" in this.$route.query) {
                this.collectionSelected = this.$route.query.collections;
            }
            if ("periods" in this.$route.query) {
                this.periodSelected = this.$route.query.periods;
            }
        }
    },
    methods: {
        search() {
            let formValues = {};
            for (let value in this.formValues) {
                if (!value.startsWith("source") || !value.startsWith("target")) {
                    formValues[value] = this.formValues[value];
                }
            }
            if (this.dateType == "range") {
                if (this.dateRange.from || this.dateRange.to) {
                    if (!this.dateRange.from) {
                        this.dateRange.from = 1700;
                    }
                    if (!this.dateRange.to) {
                        this.dateRange.to = 1800;
                    }
                    formValues.date = `${this.dateRange.from}<=>${this.dateRange.to}`;
                } else {
                    this.dateType = "exact";
                }
            }
            if (this.collectionSelected) {
                formValues.collections = this.collectionSelected;
            } else if ("collections" in formValues) {
                delete formValues.collections;
            }
            if (this.periodSelected) {
                formValues.periods = this.periodSelected;
            } else if ("periods" in formValues) {
                delete formValues.periods;
            }
            let route = this.paramsToRoute(formValues, "/search");
            this.$router.push(route);
        },
        clearForm() {
            this.formValues = {};
            this.periodSelected = null;
            this.collectionSelected = null;
            this.dateType = "exact";
            this.dateRange = {
                to: null,
                from: null,
            };
        },
        dropSelect(selection) {
            this.dateType = selection;
            if (this.dateType == "exact") {
                this.formValues.date = "";
            }
        },
        selectTopic(topic) {
            let words = topic.replace(/,/g, "");
            this.formValues.words = words;
            document.querySelector("#words input").value = words;
            this.formValues.binding = "OR";
        },
        addAssociatedWords() {
            if (this.formValues.words.split(" ").length > 1) {
                alert("This feature only works with one word in the search box");
            } else {
                this.$http
                    .get(
                        `${this.$appConfig.apiServer}/intertextual-hub-api/get_associated_words/${this.formValues.words}`
                    )
                    .then((response) => {
                        this.formValues.words = `${this.formValues.words} ${response.data
                            .map((word) => {
                                return word.word;
                            })
                            .join(" ")}`;
                        document.querySelector("#words input").value = this.formValues.words;
                        this.formValues.binding = "OR";
                    })
                    .catch(() => {
                        // alert("word is not present in associated word index");
                        this.showAlert();
                    });
            }
        },
        countDownChanged(dismissCountDown) {
            this.dismissCountDown = dismissCountDown;
        },
        showAlert() {
            this.dismissCountDown = 3;
        },
        hideForm() {
            EventBus.$emit("hideForms");
        },
    },
};
</script>
<style scoped>
.input-group-prepend,
.input-group-text {
    display: inline-flex !important;
}

::v-deep #words .dropdown-menu {
    max-height: 300px;
    overflow-y: scroll;
}
::v-deep .dropdown-item {
    padding: 0.25rem 1rem;
}
</style>
