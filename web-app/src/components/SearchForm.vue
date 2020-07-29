<template>
    <b-card class="shadow-sm mb-4 border-top-0">
        <b-form @submit.stop.prevent="search" @reset="clearForm">
            <b-input-group prepend="Words" id="words" class="pb-3">
                <b-form-input
                    v-model.lazy="formValues.words"
                    placeholder="e.g. conspirateurs aristocrates ennemis royalistes"
                ></b-form-input>
                <template v-slot:append>
                    <b-dropdown text="Select topic" right variant="outline-secondary">
                        <b-dropdown-item
                            v-for="topic in topics"
                            :key="topic.name"
                            @click="selectTopic(topic.description)"
                        >Topic {{topic.name}}: {{topic.description}}</b-dropdown-item>
                    </b-dropdown>
                </template>
            </b-input-group>
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
            <button class="btn btn-primary rounded-0" type="submit">Search</button>
            <button type="reset" class="btn btn-secondary rounded-0">Reset</button>
        </b-form>
    </b-card>
</template>
<script>
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
                ...this.$appConfig.collections,
            ],
            collectionSelected: null,
            periods: [
                { text: "All periods", value: null },
                ...this.$appConfig.periods,
            ],
            periodSelected: null,
            formValues: {},
            topics: [],
        };
    },
    created() {
        if (this.$route.query || Object.keys(this.$route.query).length > 0) {
            this.formValues = this.copyObject(this.$route.query);

            if (
                "date" in this.$route.query &&
                this.$route.query["date"].match("<=>")
            ) {
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
            this.getTopics();
        }
    },
    methods: {
        getTopics() {
            this.$http
                .get(
                    "https://anomander.uchicago.edu/topologic-api/get_config/combo?full_config=True"
                )
                .then((response) => {
                    this.topics = response.data.topics_words;
                });
        },
        search() {
            let formValues = { ...this.formValues };
            if (this.dateType == "range" && this.dateRange.from.length > 0) {
                formValues.date = `${this.dateRange.from}<=>${this.dateRange.to}`;
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
        },
        dropSelect(selection) {
            this.dateType = selection;
        },
        selectTopic(topic) {
            let words = topic.replace(/,/g, "");
            this.formValues.words = words;
            document.querySelector("#words input").value = words;
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
</style>