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
                <div
                    class="input-group pb-3"
                    v-for="field in metadataFields.source"
                    :key="field.label"
                >
                    <span class="input-group-prepend">
                        <span class="input-group-text rounded-0">
                            {{
                            field.label
                            }}
                        </span>
                    </span>
                    <input
                        type="text"
                        class="form-control rounded-0"
                        :name="field.value"
                        v-model="formValues[field.value]"
                    />
                </div>
            </b-col>
            <b-col cols="6" class="border border-top-0 border-right-0 border-bottom-0">
                <div
                    class="input-group pb-3"
                    v-for="field in metadataFields.target"
                    :key="field.label"
                >
                    <span class="input-group-prepend">
                        <span class="input-group-text rounded-0">
                            {{
                            field.label
                            }}
                        </span>
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
        <button class="btn btn-primary rounded-0" type="button" @click="search()">Search</button>
        <button type="button" class="btn btn-secondary rounded-0" @click="clearForm()">Reset</button>
    </b-card>
</template>
<script>
export default {
    name: "SimilarPassageForm",
    data() {
        return {
            metadataFields: this.$appConfig.searchFormFields,
            formValues: {}
        };
    },
    created() {
        if (this.$route.query || Object.keys(this.$route.query).length > 0) {
            this.formValues = this.copyObject(this.$route.query);
        }
    },
    methods: {
        search() {
            let route = this.paramsToRoute(this.formValues);
            this.$router.push(route);
        },
        clearForm() {
            this.formValues = {};
        }
    }
};
</script>
