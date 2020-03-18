<template>
    <b-card class="shadow">
        <b-card-text>
            <RenderString v-if="text" :string="text"></RenderString>
        </b-card-text>
        <b-modal
            id="text-reuse"
            size="xl"
            centered
            scrollable
            hide-footer
            v-if="intertextualLinks"
            title="Intertextual Links"
        >
            <div v-if="intertextualLinks.length == 1">
                <div class="row">
                    <div class="col mt-2">
                        <h6 class="text-center pb-2">Earlier Use</h6>
                        <p class="pt-3 px-3">
                            {{ intertextualLinks[0].source_author }}
                            <span class="separator">&#9679;</span>
                            <i>
                                {{ intertextualLinks[0].source_title }}
                            </i>
                            <span class="separator">&#9679;</span>
                            <span v-if="intertextualLinks[0].source_year">
                                {{ intertextualLinks[0].source_year }}
                            </span>
                        </p>
                    </div>
                    <div
                        class="col mt-2 border border-top-0 border-right-0 border-bottom-0"
                    >
                        <h6 class="text-center pb-2">Later use</h6>
                        <p class="pt-3 px-3">
                            {{ intertextualLinks[0].target_author }}
                            <span class="separator">&#9679;</span>
                            <i>
                                {{ intertextualLinks[0].target_title }}
                            </i>
                            <span class="separator">&#9679;</span>
                            <span v-if="intertextualLinks[0].target_year">
                                {{ intertextualLinks[0].target_year }}
                            </span>
                        </p>
                    </div>
                </div>
                <div class="row passages">
                    <div class="col mb-2">
                        <p class="card-text text-justify px-3 pt-2 pb-4 mb-4">
                            {{ intertextualLinks[0].source_context_before }}
                            <span class="source-passage">
                                {{ intertextualLinks[0].source_passage }}
                            </span>
                            {{ intertextualLinks[0].source_context_after }}
                        </p>
                    </div>
                    <div
                        class="col mb-2 border border-top-0 border-right-0 border-bottom-0"
                    >
                        <p class="card-text text-justify px-3 pt-2 pb-4 mb-4">
                            {{ intertextualLinks[0].target_context_before }}
                            <span class="target-passage">
                                {{ intertextualLinks[0].target_passage }}
                            </span>
                            {{ intertextualLinks[0].target_context_after }}
                        </p>
                    </div>
                </div>
            </div>
            <div v-if="intertextualLinks.length > 1">
                <h6>
                    The following passage is found in the texts cited below:
                </h6>
                <p class="my-2">
                    {{ intertextualLinks[0].target_passage }}
                </p>
                <ul>
                    <li
                        v-for="(passagePair, pairIndex) in intertextualLinks"
                        :key="pairIndex"
                    >
                        {{ passagePair.source_author }}
                        <span class="separator">&#9679;</span>
                        <i>{{ passagePair.source_title }}</i>
                        <span class="separator">&#9679;</span>
                        <span v-if="passagePair.source_year">
                            {{ passagePair.source_year }}
                        </span>
                        <a href @click="togglePassage()">See passage</a>
                    </li>
                </ul>
            </div>
        </b-modal>
        <div id="intertextual-metadata" class="shadow p-2">
            <div v-if="currentIntertextualMetadata">
                <h6>Passage found in:</h6>
                <p
                    v-for="(metadata,
                    metadataIndex) in currentIntertextualMetadata"
                    :key="metadataIndex"
                >
                    {{ metadata.author }}
                    <span class="separator">&#9679;</span>
                    {{ metadata.title }}
                    <span class="separator">&#9679;</span>
                    {{ metadata.year }}
                </p>
            </div>
        </div>
    </b-card>
</template>
<script>
import RenderString from "./RenderString.vue";
import { EventBus } from "../main.js";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/light.css";

export default {
    name: "TextNavigation",
    components: {
        RenderString
    },
    data() {
        return {
            text: null,
            intertextualLinks: null,
            highlighted: {},
            currentIntertextualMetadata: null
        };
    },
    created() {
        this.$http
            .get("https://anomander.uchicago.edu/intertextual-hub-api")
            .then(response => {
                this.text = response.data.text;
            });
        EventBus.$on("showPassage", data => {
            if (
                typeof this.highlighted[data.passageNumber] == "undefined" ||
                !this.highlighted[data.passageNumber]
            ) {
                this.$http
                    .get(
                        "https://anomander.uchicago.edu/text-pair-api/search_alignments",
                        {
                            params: {
                                db_table: "frantext18thc_vs_frc",
                                target_start_byte: data.offsets[0],
                                target_end_byte: data.offsets[1]
                            }
                        }
                    )
                    .then(response => {
                        this.intertextualLinks = response.data.alignments;
                        this.currentIntertextualMetadata = this.intertextualLinks.map(
                            alignment => ({
                                author: alignment.source_author,
                                title: alignment.source_title,
                                year: alignment.source_year
                            })
                        );

                        let link = document.createElement("span");
                        let text = document.createTextNode(" See reuses");
                        link.append(text);
                        link.title = "Intertextual links";
                        link.id = `passage-click-${data.passageNumber}`;
                        link.classList.add("intertextual-link");
                        document
                            .getElementById(`end-passage-${data.passageNumber}`)
                            .after(link);
                        document
                            .getElementById(
                                `passage-click-${data.passageNumber}`
                            )
                            .addEventListener("click", () => {
                                this.$bvModal.show("text-reuse");
                            });
                        this.$nextTick(() => {
                            tippy(data.element, {
                                content() {
                                    let popup = document.getElementById(
                                        "intertextual-metadata"
                                    );
                                    return popup.innerHTML;
                                },
                                allowHTML: true,
                                theme: "light"
                            });
                        });
                    });
                document
                    .getElementsByClassName(`passage-${data.passageNumber}`)
                    .forEach(el => {
                        el.style.color = "indianred";
                    });

                this.highlighted[data.passageNumber] = true;
            } else {
                document
                    .getElementsByClassName(`passage-${data.passageNumber}`)
                    .forEach(el => {
                        el.style.color = "initial";
                    });
                this.highlighted[data.passageNumber] = false;
                let link = document.getElementById(
                    `passage-click-${data.passageNumber}`
                );
                link.parentNode.removeChild(link);
            }
        });
    }
};
</script>
