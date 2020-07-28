<template>
    <b-card class="shadow-sm mb-4 border-top-0">
        <b-form @submit.stop.prevent="search" @reset="clearForm">
            <b-input-group prepend="Words" class="pb-3">
                <b-form-input
                    v-model="formValues.words"
                    placeholder="e.g. conspirateurs aristocrates ennemis royalistes"
                ></b-form-input>
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
            formValues: {},
            dateType: "exact",
            dateRange: {
                to: null,
                from: null,
            },
        };
    },
    methods: {
        search() {
            let formValues = { ...this.formValues };
            if (this.dateType == "range" && this.dateRange.from.length > 0) {
                formValues.date = `${this.dateRange.from}<=>${this.dateRange.to}`;
            }
            let route = this.paramsToRoute(formValues, "/search");
            this.$router.push(route);
        },
        clearForm() {
            this.formValues = {};
        },
        dropSelect(selection) {
            this.dateType = selection;
        },
    },
};
</script>
<style scoped>
.input-group-prepend,
.input-group-text {
    display: inline-flex !important;
}
</style>