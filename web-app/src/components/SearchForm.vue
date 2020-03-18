<template>
    <b-card class="shadow mb-4">
        <b-row>
            <b-col>
                <div
                    class="input-group pb-3"
                    v-for="field in metadataFields"
                    :key="field.label"
                >
                    <span class="input-group-prepend">
                        <span class="input-group-text rounded-0">{{
                            field.label
                        }}</span>
                    </span>
                    <input
                        type="text"
                        class="form-control rounded-0"
                        :name="field.value"
                        v-model="formValues[field.value]"
                    />
                </div>
            </b-col>
        </b-row>
        <button
            class="btn btn-primary rounded-0"
            type="button"
            @click="search()"
        >
            Search
        </button>
        <button
            type="button"
            class="btn btn-secondary rounded-0"
            @click="clearForm()"
        >
            Reset
        </button>
    </b-card>
</template>
<script>
export default {
    name: "SearchForm",
    data() {
        return {
            metadataFields: [
                { label: "Author", value: "source_author" },
                { label: "Title", value: "source_title" }
            ],
            formValues: {}
        };
    },
    methods: {
        search() {
            console.log(this.formValues);
        },
        clearForm() {}
    }
};
</script>
