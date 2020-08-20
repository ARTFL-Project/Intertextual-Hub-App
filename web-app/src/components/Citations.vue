<template>
    <span>
        <span v-for="(citation, citeIndex) in citations" :key="citeIndex" :style="citation.style">
            <span v-if="citation.link">
                <b-button
                    href="#"
                    tabindex="0"
                    class="link"
                    :id="`${philoDb}_${philoId}-${index}`"
                >{{ citation.field || 'Unnamed section' }}</b-button>
                <doc-link
                    :target="`${philoDb}_${philoId}-${index}`"
                    :philo-db="philoDb"
                    :philo-id="philoId"
                ></doc-link>
            </span>
            <span v-else>{{ citation.field }}</span>
            <span
                class="separator"
                v-if="
                    (citation.field.length > 0 || citation.link) &&
                        citeIndex != citations.length - 1
                "
            >&#9679;</span>
        </span>
    </span>
</template>
<script>
import DocLink from "./DocLink";

export default {
    name: "Citations",
    components: {
        DocLink,
    },
    props: ["philoDb", "docPair", "direction", "index", "nolink"],
    data() {
        return {
            fields: this.$appConfig.philoDBs[this.philoDb].citation_fields,
            objectLevel: this.$appConfig.philoDBs[this.philoDb].object_type,
        };
    },
    computed: {
        fieldPrefix() {
            if (this.direction && typeof this.direction != "undefined") {
                return `${this.direction}_`;
            }
            return "";
        },
        philoId() {
            return this.docPair[`${this.fieldPrefix}philo_id`];
        },
        citations() {
            let citations = [];
            let noDate = true;
            for (let field of this.fields) {
                let style = this.$appConfig.styles[field];
                let fieldValue = this.docPair[`${this.fieldPrefix}${field}`];
                if (typeof fieldValue != "undefined") {
                    if (field === "date" && fieldValue.endsWith("-01-01")) {
                        fieldValue = fieldValue.replace(/-01-01/, "");
                    }
                    if (field == "date") {
                        noDate = false;
                    }

                    let link = false;
                    if (typeof this.nolink == "undefined") {
                        if (this.objectLevel == "doc" && field == "title") {
                            link = true;
                        } else if (
                            this.objectLevel == "div1" &&
                            field == "head"
                        ) {
                            link = true;
                        } else if (
                            this.objectLevel == "div2" &&
                            field == "head"
                        ) {
                            link = true;
                        }
                    }

                    citations.push({
                        field: fieldValue,
                        style: style,
                        link: link,
                    });
                }
            }
            if (noDate) {
                if (typeof this.docPair.year != "undefined") {
                    citations.push({
                        field: this.docPair.year,
                        style: this.$appConfig.styles.date,
                        link: "",
                    });
                }
            }
            return citations;
        },
    },
    methods: {},
};
</script>
<style scoped>
.separator {
    display: inline-block;
    margin: 0 0.3rem;
    font-style: initial;
}
</style>
