<template>
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
                        <b-dropdown :text="sourceDateType" variant="outline-secondary">
                            <b-dropdown-item @click="dropSelect('exact', 'source')">exact</b-dropdown-item>
                            <b-dropdown-item @click="dropSelect('range', 'source')">range</b-dropdown-item>
                        </b-dropdown>
                    </template>
                    <b-form-input
                        v-model="formValues['source_date']"
                        v-if="sourceDateType == 'exact'"
                    ></b-form-input>
                    <b-form-input
                        v-model="sourceDateRange.from"
                        v-if="sourceDateType == 'range'"
                        placeholder="from"
                        class="ml-3"
                    ></b-form-input>
                    <b-form-input
                        v-model="sourceDateRange.to"
                        v-if="sourceDateType == 'range'"
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
                        <b-dropdown :text="targetDateType" variant="outline-secondary">
                            <b-dropdown-item @click="dropSelect('exact', 'target')">exact</b-dropdown-item>
                            <b-dropdown-item @click="dropSelect('range', 'target')">range</b-dropdown-item>
                        </b-dropdown>
                    </template>
                    <b-form-input
                        v-model="formValues['target_date']"
                        v-if="targetDateType == 'exact'"
                    ></b-form-input>
                    <b-form-input
                        v-model="targetDateRange.from"
                        v-if="targetDateType == 'range'"
                        placeholder="from"
                        class="ml-3"
                    ></b-form-input>
                    <b-form-input
                        v-model="targetDateRange.to"
                        v-if="targetDateType == 'range'"
                        placeholder="to"
                        class="ml-3"
                    ></b-form-input>
                </b-input-group>
            </b-col>
        </b-row>
        <button class="btn btn-primary rounded-0" type="button" @click="search()">Search</button>
        <button type="button" class="btn btn-secondary rounded-0" @click="clearForm()">Reset</button>
    </b-card>
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
            sourceDateType: "exact",
            targetDateType: "exact",
            sourceDateRange: { to: null, from: null },
            targetDateRange: { to: null, from: null }
        };
    },
    created() {
        // if (this.$route.query || Object.keys(this.$route.query).length > 0) {
        //     this.formValues = this.copyObject(this.$route.query);
        // }
    },
    methods: {
        search() {
            let formValues = { ...this.formValues };
            if (
                this.sourceDateType == "range" &&
                this.sourceDateRange.from.length > 0
            ) {
                formValues.source_date = `${this.sourceDateRange.from}<=>${this.sourceDateRange.to}`;
            }
            if (
                this.targetDateType == "range" &&
                this.targetDateRange.from.length > 0
            ) {
                formValues.target_date = `${this.targetDateRange.from}<=>${this.targetDateRange.to}`;
            }
            let route = this.paramsToRoute(formValues);
            this.$router.push(route);
        },
        clearForm() {
            this.formValues = {};
        },
        dropSelect(selection, direction) {
            if (direction == "source") {
                this.sourceDateType = selection;
            } else {
                this.targetDateType = selection;
            }
        }
    }
};
</script>
