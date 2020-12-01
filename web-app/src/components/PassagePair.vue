<template>
    <b-row :id="passage.passageid" class="mb-4">
        <b-col cols="6" class="mt-2" v-if="passage.metadata">
            <h6 class="text-center pb-2">Earlier Use</h6>
            <p class="pt-3 px-3">
                <citations :docPair="passage.metadata" direction="source" :philo-db="sourcePhiloDb"></citations>
            </p>
            <b-button class="ml-3 mb-2" size="sm" variant="outline-secondary" @click="goToDocument(passage, 'source')">
                See
                <span v-if="message">{{ message }}</span>
                <span v-else>{{ "this" | pluralize(passageNumber) }} {{ "passage" | pluralize(passageNumber) }}</span>
                in document
            </b-button>
        </b-col>
        <b-col cols="6" class="mt-2 border border-top-0 border-right-0 border-bottom-0" v-if="passage.metadata">
            <h6 class="text-center pb-2">Later use</h6>
            <p class="pt-3 px-3">
                <citations :docPair="passage.metadata" direction="target" :philo-db="targetPhiloDb"></citations>
            </p>
            <b-button class="ml-3" size="sm" variant="outline-secondary" @click="goToDocument(passage, 'target')">
                See
                <span v-if="message">{{ message }}</span>
                <span v-else>{{ "this" | pluralize(passageNumber) }} {{ "passage" | pluralize(passageNumber) }}</span>
                in document
            </b-button>
        </b-col>
        <b-col cols="6" class="mb-2 text">
            <p class="card-text text-justify px-3 pt-2 mb-4">
                {{ passage.source_context_before }}
                <span class="source-passage">{{ passage.source_passage }}</span>
                {{ passage.source_context_after }}
            </p>
        </b-col>
        <b-col cols="6" class="mb-2 border border-top-0 border-right-0 border-bottom-0 text">
            <p class="card-text text-justify px-3 pt-2 mb-4">
                {{ passage.target_context_before }}
                <span class="target-passage">{{ passage.target_passage }}</span>
                {{ passage.target_context_after }}
            </p>
        </b-col>
        <div class="text-center" style="width: 100%">
            <a
                class="diff-btn"
                diffed="false"
                @click="
                    showDifferences(
                        passage.source_passage,
                        passage.target_passage,
                        passage.source_passage.length,
                        passage.target_passage.length
                    )
                "
                >Show differences</a
            >
            <div class="loading position-absolute" style="display: none; left: 50%; transform: translateX(-50%)">
                <atom-spinner :animation-duration="800" :size="25" color="#000" />
            </div>
        </div>
    </b-row>
</template>

<script>
import Citations from "./Citations";
import { AtomSpinner } from "epic-spinners";
import Worker from "worker-loader!./diffStrings";

export default {
    name: "PassagePair",
    components: { Citations, AtomSpinner },
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
                        pairid: this.pairid || this.passage.metadata.pairid,
                        direction: direction,
                    },
                    `/navigate/${this.sourcePhiloDb}/${this.sourcePhiloId.split(" ").join("/")}`
                );
            } else {
                link = this.paramsToRoute(
                    {
                        pairid: this.pairid || this.passage.metadata.pairid,
                        direction: direction,
                    },
                    `/navigate/${this.targetPhiloDb}/${this.targetPhiloId.split(" ").join("/")}`
                );
            }
            this.$router.push(link);
        },
        showDifferences(sourceText, targetText, sourcePassageLength, targetPassageLength) {
            if (sourcePassageLength > 50000 || targetPassageLength > 50000) {
                alert("Passage of 50000 words or more may take up a long time to compare");
            }

            let parent = document.getElementById(this.passage.passageid);
            let loading = parent.querySelector(".loading");
            let sourceElement = parent.querySelector(".source-passage");
            let targetElement = parent.querySelector(".target-passage");
            if (event.srcElement.getAttribute("diffed") == "false") {
                loading.style.display = "initial";
                let outerEvent = event;
                this.worker = new Worker();
                this.worker.postMessage([sourceText, targetText]);
                this.worker.onmessage = function (response) {
                    let differences = response.data;
                    let newSourceString = "";
                    let newTargetString = "";
                    for (let diffObj of differences) {
                        let [diffCode, text] = diffObj;
                        if (diffCode === 0) {
                            newSourceString += text;
                            newTargetString += text;
                        } else if (diffCode === -1) {
                            newSourceString += `<span class="removed">${text}</span>`;
                        } else if (diffCode === 1) {
                            newTargetString += `<span class="added">${text}</span>`;
                        }
                    }
                    sourceElement.innerHTML = newSourceString;
                    targetElement.innerHTML = newTargetString;
                    outerEvent.srcElement.setAttribute("diffed", "true");
                    loading.style.display = "none";
                    outerEvent.srcElement.textContent = "Hide differences";
                };
            } else {
                sourceElement.innerHTML = sourceText;
                targetElement.innerHTML = targetText;
                event.srcElement.setAttribute("diffed", "false");
                event.srcElement.textContent = "Show differences";
            }
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
    color: indianred;
}
.diff-btn {
    display: inline-block;
    padding: 0.3rem;
    margin-bottom: 2px;
    border: solid 1px #ddd;
    cursor: pointer;
    font-size: 90%;
    text-decoration: none !important;
}
.diff-btn:hover {
    color: #565656 !important;
    background-color: #f8f8f8;
}
::v-deep .added {
    color: maroon;
    font-weight: 700;
}
::v-deep .removed {
    color: seagreen;
    font-weight: 700;
    text-decoration: line-through;
}
</style>