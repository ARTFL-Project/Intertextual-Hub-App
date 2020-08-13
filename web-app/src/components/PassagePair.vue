<template>
    <b-row>
        <b-col cols="6" class="mt-2" v-if="passage.metadata">
            <h6 class="text-center pb-2">Earlier Use</h6>
            <p class="pt-3 px-3">
                <citations :docPair="passage.metadata" direction="source" :philo-db="sourcePhiloDb"></citations>
            </p>
            <b-button
                class="ml-3 mb-2"
                size="sm"
                variant="outline-secondary"
                @click="goToDocument(passage, 'source')"
            >
                See
                <span v-if="message">{{message}}</span>
                <span
                    v-else
                >{{"this" | pluralize(passageNumber)}} {{'passage' | pluralize(passageNumber)}}</span> in document
            </b-button>
        </b-col>
        <b-col
            cols="6"
            class="mt-2 border border-top-0 border-right-0 border-bottom-0"
            v-if="passage.metadata"
        >
            <h6 class="text-center pb-2">Later use</h6>
            <p class="pt-3 px-3">
                <citations :docPair="passage.metadata" direction="target" :philo-db="targetPhiloDb"></citations>
            </p>
            <b-button
                class="ml-3"
                size="sm"
                variant="outline-secondary"
                @click="goToDocument(passage, 'target')"
            >
                See
                <span v-if="message">{{message}}</span>
                <span
                    v-else
                >{{"this" | pluralize(passageNumber)}} {{'passage' | pluralize(passageNumber)}}</span> in document
            </b-button>
        </b-col>
        <b-col cols="6" class="mb-2">
            <p class="card-text text-justify px-3 pt-2 pb-4 mb-4">
                {{ passage.source_context_before }}
                <span
                    class="source-passage"
                >{{ passage.source_passage }}</span>
                {{ passage.source_context_after }}
            </p>
        </b-col>
        <b-col cols="6" class="mb-2 border border-top-0 border-right-0 border-bottom-0">
            <p class="card-text text-justify px-3 pt-2 pb-4 mb-4">
                {{ passage.target_context_before }}
                <span
                    class="target-passage"
                >{{ passage.target_passage }}</span>
                {{ passage.target_context_after }}
            </p>
        </b-col>
    </b-row>
</template>

<script>
import Citations from "./Citations";
export default {
    name: "PassagePair",
    components: { Citations },
    props: [
        "passage",
        "sourcePhiloDb",
        "sourcePhiloId",
        "targetPhiloDb",
        "targetPhiloId",
        "passageNumber",
        "pairid",
        "message",
    ],
    created() {
        if ("metadata" in this.passage) {
            this.passage.metadata.source_philo_id = this.sourcePhiloId;
            this.passage.metadata.target_philo_id = this.targetPhiloId;
        }
    },
    methods: {
        goToDocument(documentPair, direction) {
            let link;
            if (direction == "source") {
                link = this.paramsToRoute(
                    {
                        pairid: this.pairid,
                        direction: direction,
                    },
                    `/navigate/${this.sourcePhiloDb}/${this.sourcePhiloId
                        .split(" ")
                        .join("/")}`
                );
            } else {
                link = this.paramsToRoute(
                    {
                        pairid: this.pairid,
                        direction: direction,
                    },
                    `/navigate/${this.targetPhiloDb}/${this.targetPhiloId
                        .split(" ")
                        .join("/")}`
                );
            }
            this.$router.push(link);
        },
    },
};
</script>
<style scoped>
.separator {
    display: inline-block;
    padding: 0 0.5rem;
    font-size: 0.5rem;
    vertical-align: middle;
}
.source-passage,
.target-passage {
    color: dodgerblue;
}
</style>