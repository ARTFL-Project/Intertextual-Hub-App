<template>
    <div class="d-inline-block">
        <span
            v-for="(citation, citeIndex) in citations"
            :key="citation.field"
            :style="citation.style"
        >
            <router-link v-if="citation.link" :to="docLink()">
                {{
                citation.field || "Unnamed section"
                }}
            </router-link>
            <span v-else>{{ citation.field }}</span>
            <span class="separator" v-if="citeIndex != citations.length - 1">&#9679;</span>
        </span>

        <br />
        <!-- <a :href="goToPhilo()" target="_blank" v-if="doc.philo_type">Navigate to full text</a> -->
    </div>
</template>
<script>
export default {
    name: "Citations",
    props: ["philoDb", "docPair", "direction"],
    data() {
        return {
            fields: ["author", "title", "head", "date"],
            filteredToKeep: this.$hubConfig.philoDBs[this.philoDb]
                .citation_fields
        };
    },
    computed: {
        citations() {
            let citations = [];
            for (let field of this.fields) {
                let style = this.$appConfig.styles[field];
                let fieldValue = this.docPair[`${this.direction}_${field}`];
                if (field === "date" && fieldValue.endsWith("-01-01")) {
                    fieldValue = fieldValue.replace(/-01-01/, "");
                }
                citations.push({
                    field: fieldValue,
                    style: style,
                    link: ""
                });
            }
            return citations;
        }
    },
    methods: {
        docLink() {
            // let philoType = `philo_${this.doc.metadata.philo_type}_id`;
            // let url = `/document/${this.philoDb}/${this.doc.metadata[philoType]
            //     .split(" ")
            //     .join("/")}`;
            // return url;
            return "";
        },
        goToPhilo() {
            // let philoType = `philo_${this.doc.metadata.philo_type}_id`;
            // if (this.doc.metadata.philo_type == "doc") {
            //     return `${this.philoUrl}/navigate/${this.doc.metadata[philoType]}/table-of-contents/`;
            // } else {
            //     let objectId = this.doc.metadata[philoType]
            //         .split(" ")
            //         .join("/");
            //     return `${this.philoUrl}/navigate/${objectId}/`;
            // }
            return "";
        }
    }
};
</script>
<style scoped>
.separator {
    display: inline-block;
    margin: 0 0.25rem;
    font-style: italic;
}
a:not([href]) {
    color: #55acee;
    cursor: pointer;
}
a:not([href]):hover {
    color: #55acee;
    text-decoration: underline;
}
</style>