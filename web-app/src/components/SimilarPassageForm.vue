<template>
    <b-form @submit.stop.prevent="search" @reset="clearForm">
        <b-card class="shadow-sm mb-4 border-top-0">
            <b-row>
                <b-col cols="6">
                    <h6 class="text-center pb-2">Source</h6>
                </b-col>
                <b-col cols="6" class="border border-top-0 border-right-0 border-bottom-0">
                    <h6 class="text-center pb-2">Target</h6>
                </b-col>
                <b-col cols="6">
                    <b-input-group
                        :prepend="field.label"
                        class="pb-3"
                        v-for="field in metadataFields.source"
                        :key="field.label"
                    >
                        <b-form-input v-model="formValues[field.value]"></b-form-input>
                    </b-input-group>
                    <b-input-group class="pb-3">
                        <template v-slot:prepend>
                            <b-input-group-text>Date</b-input-group-text>
                            <b-dropdown :text="dateType.source" variant="outline-secondary">
                                <b-dropdown-item @click="dropSelect('exact', 'source')">exact</b-dropdown-item>
                                <b-dropdown-item @click="dropSelect('range', 'source')">range</b-dropdown-item>
                            </b-dropdown>
                        </template>
                        <b-form-input
                            v-model="formValues['source_date']"
                            v-if="dateType.source == 'exact'"
                        ></b-form-input>
                        <b-form-input
                            v-model="dateRange.source.from"
                            v-if="dateType.source == 'range'"
                            placeholder="from"
                            class="ml-3"
                        ></b-form-input>
                        <b-form-input
                            v-model="dateRange.source.to"
                            v-if="dateType.source == 'range'"
                            placeholder="to"
                            class="ml-3"
                        ></b-form-input>
                    </b-input-group>
                </b-col>
                <b-col cols="6" class="border border-top-0 border-right-0 border-bottom-0">
                    <b-input-group
                        :prepend="field.label"
                        class="pb-3"
                        v-for="field in metadataFields.target"
                        :key="field.label"
                    >
                        <b-form-input v-model="formValues[field.value]"></b-form-input>
                    </b-input-group>
                    <b-input-group class="pb-3">
                        <template v-slot:prepend>
                            <b-input-group-text>Date</b-input-group-text>
                            <b-dropdown :text="dateType.target" variant="outline-secondary">
                                <b-dropdown-item @click="dropSelect('exact', 'target')">exact</b-dropdown-item>
                                <b-dropdown-item @click="dropSelect('range', 'target')">range</b-dropdown-item>
                            </b-dropdown>
                        </template>
                        <b-form-input
                            v-model="formValues['target_date']"
                            v-if="dateType.target == 'exact'"
                        ></b-form-input>
                        <b-form-input
                            v-model="dateRange.target.from"
                            v-if="dateType.target == 'range'"
                            placeholder="from"
                            class="ml-3"
                        ></b-form-input>
                        <b-form-input
                            v-model="dateRange.target.to"
                            v-if="dateType.target == 'range'"
                            placeholder="to"
                            class="ml-3"
                        ></b-form-input>
                    </b-input-group>
                </b-col>
            </b-row>
            <button class="btn btn-primary rounded-0" type="submit">Search</button>
            <button type="reset" class="btn btn-secondary rounded-0">Reset</button>
        </b-card>
    </b-form>
</template>
<script>
export default {
    name: "SimilarPassageForm",
    data() {
        return {
            metadataFields: {
                source: [
                    {
                        label: "Author",
                        value: "source_author"
                    },
                    {
                        label: "Title",
                        value: "source_title"
                    }
                ],
                target: [
                    {
                        label: "Author",
                        value: "target_author"
                    },
                    {
                        label: "Title",
                        value: "target_title"
                    }
                ]
            },
            formValues: {},
            dateType: {
                source: "exact",
                target: "exact"
            },
            dateRange: {
                source: { to: null, from: null },
                target: { to: null, from: null }
            }
        };
    },
    created() {
        if (this.$route.query || Object.keys(this.$route.query).length > 0) {
            this.formValues = this.copyObject(this.$route.query);
            for (let direction of ["source", "target"]) {
                if (
                    `${direction}_date` in this.$route.query &&
                    this.$route.query[`${direction}_date`].match("<=>")
                ) {
                    this.dateType[direction] = "range";
                    let splitDates = this.$route.query[
                        `${direction}_date`
                    ].split("<=>");
                    this.dateRange[direction].from = splitDates[0];
                    this.dateRange[direction].to = splitDates[1];
                }
            }
        }
    },
    methods: {
        search() {
            console.log(this.formValues);
            delete this.formValues.direction;
            let formValues = { ...this.formValues };
            if (
                this.dateType.source == "range" &&
                this.dateRange.source.from.length > 0
            ) {
                formValues.source_date = `${this.dateRange.source.from}<=>${this.dateRange.source.to}`;
            }
            if (
                this.dateType.target == "range" &&
                this.dateRange.target.from.length > 0
            ) {
                formValues.target_date = `${this.dateRange.target.from}<=>${this.dateRange.target.to}`;
            }
            let route = this.paramsToRoute(formValues, "/seq-pair/search");
            this.$router.push(route);
        },
        clearForm() {
            this.formValues = {};
        },
        dropSelect(selection, direction) {
            if (direction == "source") {
                this.dateType.source = selection;
            } else {
                this.dateType.target = selection;
                187;
            }
        }
    }
};
</script>
