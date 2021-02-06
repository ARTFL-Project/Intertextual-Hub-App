<template>
    <div class="my-4">
        <h5 class="text-center mb-4">
            <citations :docPair="docMetadata" :direction="direction" :philo-db="philoDb" v-if="docMetadata"></citations>
        </h5>
        <b-card no-body class="shadow-sm mt-4">
            <b-tabs card v-model="tabIndex">
                <b-tab title="Similar documents" :active="!intertextual" @click="updateTocButton()">
                    <div
                        v-if="simDocsloading"
                        class="text-center"
                        style="position: absolute; left: 0; right: 0; z-index: 10"
                    >
                        <b-spinner
                            label="Loading..."
                            style="width: 2.5rem; height: 2.5rem; color: rgba(143, 57, 49, 0.8)"
                        ></b-spinner>
                    </div>
                    <div v-if="similarDocs.length > 0">
                        <h6 class="pt-2 px-2">20 most similar documents (top 5 displayed):</h6>
                        <ul class="mb-1">
                            <li
                                v-for="simDoc in simDocsToDisplay"
                                :key="`${simDoc.philo_db}${simDoc.metadata.philo_id}`"
                                style="padding: 0.15rem 0"
                            >
                                <citations :docPair="simDoc.metadata" :philo-db="simDoc.philo_db"></citations>
                            </li>
                        </ul>
                        <span
                            style="diplay: inline-block; color: rgb(143, 57, 49); cursor: pointer"
                            v-if="!showAllSimDocs"
                            @click="toggleSimDocs()"
                            >View all</span
                        >
                    </div>
                    <h6 class="p-2" v-else>No similar docs were found.</h6>
                </b-tab>
                <b-tab
                    :title="sourceReuseCount > 0 || targetReuseCount > 0 ? 'Text reuses' : 'No text reuses'"
                    :active="intertextual == 'true'"
                    :disabled="sourceReuseCount == 0 && targetReuseCount == 0"
                    @click="reUseTab()"
                >
                    <div id="direction-toggle">
                        <b-form-group @change.native="toggleDirection">
                            <b-form-radio
                                v-model="direction"
                                name="direction"
                                value="target"
                                v-if="targetReuseCount > 0"
                                >View reuses from earlier texts</b-form-radio
                            >
                            <b-form-radio
                                v-model="direction"
                                name="direction"
                                value="source"
                                v-if="sourceReuseCount > 0"
                                >View reuses in later texts</b-form-radio
                            >
                        </b-form-group>
                    </div>
                    <div v-if="docsCited">
                        <h6 class="pt-4">Reuses from these documents:</h6>
                        <ul style="padding-inline-start: 2rem; line-height: 2rem">
                            <li v-for="(doc, docIndex) in docsCited" :key="docIndex" :id="`reuse-${docIndex}`">
                                <span v-if="doc.doc_metadata[`${doc.direction}_author`]"
                                    >{{ doc.doc_metadata[`${doc.direction}_author`] }}&nbsp;&#9679;&nbsp;</span
                                >
                                <i class="docs-cited" @click="showHeads(docIndex)">{{
                                    doc.doc_metadata[`${doc.direction}_title`]
                                }}</i>
                                &nbsp;&#9679;&nbsp;
                                {{ doc.doc_metadata[`${doc.direction}_date`] }}
                                <ul style="display: none">
                                    <h6 style="margin-left: -2.5rem; padding-bottom: 0">
                                        Passages listed in order of occurrence in document:
                                    </h6>
                                    <li
                                        v-for="(metadata, metadataIndex) in doc.metadata"
                                        :key="metadata.passageid"
                                        @click="goToPassage(metadata.passageid)"
                                        style="line-height: 1.5rem"
                                    >
                                        {{ metadata[`${doc.direction}_head`] }}:
                                        <span class="docs-cited-heads">passage {{ metadataIndex + 1 }}</span>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                    <div class="p-2" v-if="intertextual && !docsCited">
                        No reuses from
                        <span v-if="direction == 'source'">later</span>
                        <span v-if="direction == 'target'">earlier</span>
                        texts were found.
                    </div>
                </b-tab>
            </b-tabs>
        </b-card>
        <b-card no-body class="mt-4 pt-3 shadow-sm" v-if="accessGranted">
            <div style="font-size: 80%; text-align: center">
                To look up a word in a dictionary, select the word and press 'd' on your keyboard.
            </div>
            <div style="font-size: 80%; text-align: center">
                To find documents similar to a particular passage, select the passage and press 's' on your keyboard.
            </div>
            <b-row id="toc-wrapper" class="text-center mt-1" v-if="loading === false">
                <div id="toc-top-bar">
                    <div id="nav-buttons" v-scroll="handleScroll">
                        <b-button variant="primary" id="back-to-top" size="sm" @click="backToTop()">
                            <span class="d-xs-none d-sm-inline-block">Back to top</span>
                            <span class="d-xs-inline-block d-sm-none">Top</span>
                        </b-button>
                        <b-button-group size="sm" style="pointer-events: all">
                            <b-button disabled="disabled" id="prev-obj" variant="primary" @click="goToTextObject(prev)"
                                >&lt;</b-button
                            >
                            <b-button
                                id="show-toc"
                                disabled="disabled"
                                variant="primary"
                                @click="toggleTableOfContents()"
                                >Table of contents</b-button
                            >
                            <b-button disabled="disabled" id="next-obj" variant="primary" @click="goToTextObject(next)"
                                >&gt;</b-button
                            >
                        </b-button-group>
                    </div>
                    <div id="toc">
                        <div id="toc-titlebar" class="d-none">
                            <b-button id="hide-toc" @click="toggleTableOfContents()">X</b-button>
                        </div>
                        <transition name="slide-fade">
                            <b-card
                                no-body
                                id="toc-content"
                                class="p-3 shadow"
                                :style="tocHeight"
                                :scroll-to="tocPosition"
                                v-if="tocOpen"
                            >
                                <div class="toc-more before" v-if="start !== 0">
                                    <b-button size="sm" variant="primary" @click="loadBefore()"></b-button>
                                </div>
                                <div v-for="(element, tocIndex) in tocElementsToDisplay" :key="tocIndex">
                                    <div
                                        :id="element.philo_id"
                                        :class="'toc-' + element.philo_type"
                                        @click="textObjectSelection(element.philo_id, tocIndex)"
                                    >
                                        <span :class="'bullet-point-' + element.philo_type"></span>
                                        <a
                                            :class="{
                                                'current-obj': element.philo_id === currentPhiloId,
                                            }"
                                            href
                                        >
                                            {{ element.label }}
                                        </a>
                                    </div>
                                </div>
                                <div class="toc-more after" v-if="end < tocElements.length">
                                    <b-button type="button" size="sm" variant="primary" @click="loadAfter()"></b-button>
                                </div>
                            </b-card>
                        </transition>
                    </div>
                </div>
            </b-row>
            <b-card-text class="mt-2 p-3 text-justify">
                <div id="previous-pages" v-if="beforeObjImgs">
                    <span class="xml-pb-image">
                        <a
                            :href="img[0]"
                            :large-img="img[1]"
                            class="page-image-link"
                            v-for="(img, imageIndex) in beforeObjImgs"
                            :key="imageIndex"
                            data-gallery
                        ></a>
                    </span>
                </div>
                <div id="previous-graphics" v-if="beforeGraphicsImgs">
                    <a
                        :href="img[0]"
                        :large-img="img[1]"
                        class="inline-img"
                        v-for="(img, beforeIndex) in beforeGraphicsImgs"
                        :key="beforeIndex"
                        data-gallery
                    ></a>
                </div>
                <div
                    id="main-text"
                    class="text"
                    v-html="text"
                    @keydown="lookUp($event, docMetadata)"
                    tabindex="0"
                ></div>
                <div id="next-pages" v-if="afterObjImgs">
                    <span class="xml-pb-image">
                        <a
                            :href="img[0]"
                            :large-img="img[1]"
                            class="page-image-link"
                            v-for="(img, afterIndex) in afterObjImgs"
                            :key="afterIndex"
                            data-gallery
                        ></a>
                    </span>
                </div>
                <div id="next-graphics" v-if="afterGraphicsImgs">
                    <a
                        :href="img[0]"
                        :large-img="img[1]"
                        class="inline-img"
                        v-for="(img, afterGraphIndex) in afterGraphicsImgs"
                        :key="afterGraphIndex"
                        data-gallery
                    ></a>
                </div>
            </b-card-text>
            <b-modal id="text-reuse" size="xl" centered scrollable hide-footer title="Intertextual Links">
                <div v-if="intertextualPassages">
                    <passage-pair
                        v-for="passage in intertextualPassages"
                        :key="passage.passageid"
                        :passage="passage"
                        :source-philo-id="passage.metadata.source_philo_id"
                        :source-philo-db="passage.metadata.source_philo_db"
                        :target-philo-id="passage.metadata.target_philo_id"
                        :target-philo-db="passage.metadata.target_philo_db"
                        message="all reuses in current text"
                        :pairid="pairid || passage.pairid"
                    ></passage-pair>
                </div>
            </b-modal>
            <div
                :id="`intertextual-metadata-${groupIndex}`"
                class="shadow px-2 pt-2 d-none"
                v-for="(_, groupIndex) in intertextualMetadata"
                :key="groupIndex"
            >
                <div v-if="intertextualMetadata">
                    <h6 class="mb-3">
                        <strong>Passage found in:</strong>
                    </h6>
                    <div class="px-2" v-for="(metadata, index) in intertextualMetadata[groupIndex]" :key="index">
                        <citations
                            :docPair="metadata"
                            direction="source"
                            :philo-db="metadata.source_philo_db"
                            v-if="direction == 'target'"
                            nolink
                            >-</citations
                        >
                        <citations
                            :docPair="metadata"
                            direction="target"
                            :philo-db="metadata.target_philo_db"
                            nolink
                            v-else
                        ></citations>
                        <hr class="m-2" v-if="index != intertextualMetadata[groupIndex].length - 1" />
                    </div>
                </div>
                <p class="mt-3 mb-0">
                    <strong>Click on passage to see reuse.</strong>
                </p>
            </div>
        </b-card>
        <access-control v-else></access-control>
        <div
            id="blueimp-gallery"
            class="blueimp-gallery blueimp-gallery-controls"
            data-full-screen="true"
            data-continuous="false"
            style="display: none"
        >
            <div class="slides"></div>
            <h3 class="title"></h3>
            <a class="prev img-buttons"></a>
            <a class="next img-buttons"></a>
            <a id="full-size-image" class="img-buttons">&nearr;</a>
            <a class="close img-buttons"></a>
            <ol class="indicator"></ol>
        </div>
        <b-modal
            id="similar-docs"
            size="xl"
            centered
            scrollable
            hide-footer
            title="Documents similar to highlighted passage"
        >
            <div v-if="passageSimilarDocs">
                <h6 class="pt-2 px-2">20 most similar documents:</h6>
                <ul>
                    <li
                        v-for="simDoc in passageSimilarDocs"
                        :key="`${simDoc.philo_db}${simDoc.metadata.philo_id}`"
                        style="padding: 0.15rem 0"
                    >
                        <citations :docPair="simDoc.metadata" :philo-db="simDoc.philo_db"></citations>
                    </li>
                </ul>
            </div>
        </b-modal>
    </div>
</template>
<script>
const PassagePair = () => import("./PassagePair.vue");
import Citations from "./Citations.vue";
const AccessControl = () => import("./AccessControl");
import Gallery from "blueimp-gallery";
import "blueimp-gallery/css/blueimp-gallery.min.css";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
import "tippy.js/themes/light-border.css";
import "tippy.js/animations/scale.css";

export default {
    name: "TextNavigation",
    components: {
        PassagePair,
        Citations,
        AccessControl,
    },
    data() {
        return {
            text: null,
            intertextualPassages: null,
            intertextualMetadata: null,
            currentIntertextualMetadata: null,
            docMetadata: null,
            alreadyScrolled: false,
            philoDb: null,
            pairid: this.$route.query.pairid,
            direction: this.$route.query.direction,
            updatedText: false,
            reload: false,
            tippyInstances: [],
            docsCited: [],
            beforeObjImgs: [],
            afterObjImgs: [],
            beforeGraphicsImgs: [],
            afterGraphicsImgs: [],
            navbar: null,
            loading: false,
            tocOpen: false,
            done: false,
            authorized: true,
            textObjectURL: "",
            philoID: "",
            highlight: false,
            start: 0,
            end: 0,
            tocPosition: 0,
            navButtonPosition: 0,
            navBarVisible: false,
            gallery: null,
            tocElements: [],
            prev: null,
            next: null,
            similarDocs: [],
            passageSimilarDocs: [],
            showAllSimDocs: false,
            objectType: null,
            sourceReuseCount: 0,
            targetReuseCount: 0,
            tabIndex: 0,
            simDocsloading: false,
            accessGranted: true,
            lastDocId: null,
            objectLevels: Object.fromEntries(
                Object.entries(this.$appConfig.philoDBs).map((values) => [values[0], values[1].object_type])
            ),
        };
    },
    computed: {
        dbPrefix: function () {
            if (this.direction) {
                return `${this.direction}_`;
            } else {
                return "";
            }
        },
        intertextual: function () {
            return this.$route.query.intertextual;
        },
        philoUrl: function () {
            return this.$appConfig.philoDBs[this.$route.params.philoDb].url;
        },
        tocElementsToDisplay: function () {
            return this.tocElements.elements.slice(this.start, this.end);
        },
        tocHeight() {
            return `max-height: ${window.innerHeight - 200}`;
        },
        simDocsToDisplay() {
            if (!this.showAllSimDocs) {
                return this.similarDocs.slice(0, 5);
            } else {
                return this.similarDocs;
            }
        },
        philoObjectType() {
            let philoId = this.getPhiloId().split(" ");
            let objectLevels = { 1: "doc", 2: "div1", 3: "div2", 4: "div3", 9: "page" };
            let objectLevel = objectLevels[philoId.length];
            return objectLevel;
        },
    },
    watch: {
        $route: "fetchData",
    },
    created() {
        this.fetchData();
    },
    mounted() {
        this.updateTocButton("mounted");
    },
    updated() {
        if (this.gallery) {
            this.$nextTick(() => {
                for (let imageType of ["page-image-link", "inline-img", "external-img"]) {
                    document.getElementById("full-size-image").removeEventListener("click", () => {
                        let imageIndex = this.gallery.getIndex();
                        let img = Array.from(document.getElementsByClassName(imageType))[imageIndex].getAttribute(
                            "large-img"
                        );
                        window.open(img);
                    });
                }
            });
        }
        this.updateInit();
    },
    destroyed() {
        let passageMarkers = document.getElementsByClassName("passage-marker");
        for (let i = 0; i < passageMarkers.length; i += 1) {
            let passageNumber = i;
            document.getElementsByClassName(`passage-${passageNumber}`).forEach((el) => {
                el.removeEventListener("click");
            });
        }
        this.tippyInstances.forEach((instance) => {
            instance.destroy();
        });
        this.tippyInstances.length = 0;
        if (this.gallery) {
            this.gallery.close();
        }
    },
    methods: {
        fetchData() {
            this.accessGranted = true;
            if (this.getPhiloId() != this.lastDocId) {
                this.fetchToC();
            }
            this.fetchPassage();
        },
        fetchPassage() {
            this.$bvModal.hide("similar-docs");
            this.text = null;
            this.docMetadata = null;
            this.docsCited = [];
            this.alreadyScrolled = false;
            this.showAllSimDocs = false;
            this.similarDocs = [];
            this.$bvModal.hide("text-reuse");
            let philoId;
            if (
                this.philoObjectType != this.objectLevels[this.$route.params.philoDb] &&
                this.$route.params.doc.split("/").length < 7
            ) {
                //catching cases where a philo_virtual is the object we want
                philoId = `${this.$route.params.doc.split("/").join(" ").trim()} 1`;
            } else {
                philoId = this.getPhiloId();
            }
            this.lastDocId = philoId;
            this.pairid = this.$route.query.pairid;
            this.$http
                .get(`${this.$appConfig.apiServer}/intertextual-hub-api/get_text/${this.$route.params.philoDb}`, {
                    params: {
                        philo_id: philoId,
                        pairid: this.$route.query.pairid,
                        direction: this.$route.query.direction,
                        intertextual: this.$route.query.intertextual,
                        byte: this.$route.query.byte,
                    },
                    withCredentials: true,
                })
                .then((response) => {
                    this.text = response.data.text;
                    this.objectType = response.data.object_type;
                    this.direction = this.$route.query.direction;
                    if (this.$route.query.direction) {
                        this.philoDb = response.data.doc_metadata[`${this.dbPrefix}philo_db`];
                    } else {
                        this.philoDb = response.data.doc_metadata.philo_db;
                    }
                    this.docMetadata = response.data.doc_metadata;
                    this.intertextualMetadata = response.data.intertextual_metadata;
                    this.docsCited = response.data.docs_cited;
                    if (!this.deepEqual(response.data.imgs, {})) {
                        this.insertPageLinks(response.data.imgs);
                        this.insertInlineImgs(response.data.imgs);
                    }
                    this.prev = response.data.prev;
                    this.next = response.data.next;
                    this.setUpNavBar();
                    this.$nextTick(() => {
                        this.setUpGallery();
                    });
                    if (this.reload) {
                        this.$nextTick(() => {
                            this.updateInit();
                        });
                    }
                })
                .catch((error) => {
                    console.log(error);
                    this.accessGranted = false;
                });
            this.$http
                .get(
                    `${this.$appConfig.apiServer}/intertextual-hub-api/check_for_alignments/${this.$route.params.philoDb}`,
                    {
                        params: {
                            philo_id: philoId,
                        },
                    }
                )
                .then((response) => {
                    this.sourceReuseCount = response.data.source_count;
                    this.targetReuseCount = response.data.target_count;
                });
            this.simDocsloading = true;
            this.$http
                .get(
                    `${this.$appConfig.apiServer}/intertextual-hub-api/get_similar_docs/${this.$route.params.philoDb}`,
                    {
                        params: {
                            philo_id: philoId,
                        },
                    }
                )
                .then((response) => {
                    this.simDocsloading = false;
                    this.similarDocs = response.data;
                });
        },
        getPhiloId() {
            let philoId = [];
            if (this.$route.params.doc.split("/").length == 9) {
                return this.$route.params.doc.split("/").join(" ");
            }
            for (let id of this.$route.params.doc.split("/")) {
                if (id == "0") {
                    break;
                }
                philoId.push(id);
            }
            return philoId.join(" ");
        },
        showPassage(element) {
            if (!element.id.startsWith("end-passage")) {
                let passageNumber = element.getAttribute("n");
                var getAlignments;
                if (!("intertextual" in this.$route.query)) {
                    let offsets = element.dataset.offsets.split("-");
                    getAlignments = () => {
                        this.getAlignment({
                            offsets: offsets,
                            passageNumber: passageNumber,
                            element: element,
                        });
                    };
                } else {
                    getAlignments = () => {
                        let passagesMetadata = this.intertextualMetadata[parseInt(passageNumber)];
                        this.getAlignments(
                            passagesMetadata.map((metadata) => {
                                return metadata.pairid;
                            }),
                            passagesMetadata.map((metadata) => {
                                return metadata.passageid;
                            }),
                            passagesMetadata
                        );
                    };
                }
                document.getElementsByClassName(`passage-${passageNumber}`).forEach((el) => {
                    el.addEventListener("click", getAlignments, false);
                });
            }
        },
        getAlignment(data) {
            this.$http
                .get(`${this.$appConfig.apiServer}/intertextual-hub-api/retrieve_passage/${this.$route.query.pairid}`, {
                    params: {
                        start_byte: data.offsets[0],
                        direction: this.$route.query.direction,
                    },
                })
                .then((response) => {
                    this.intertextualPassages = [
                        {
                            ...response.data,
                            metadata: {
                                ...this.intertextualMetadata[0][0],
                                ...this.docMetadata,
                            },
                        },
                    ];
                    this.$bvModal.show("text-reuse");
                });
        },
        getAlignments(pairids, passageids, passagesMetadata) {
            this.$http
                .post(`${this.$appConfig.apiServer}/intertextual-hub-api/retrieve_passages_all/`, {
                    pairids: pairids,
                    passageids: passageids,
                })
                .then((response) => {
                    let intertextualPassages = [];
                    for (let i = 0; i < passagesMetadata.length; i += 1) {
                        intertextualPassages.push({
                            ...response.data[i],
                            metadata: {
                                ...passagesMetadata[i],
                                ...this.docMetadata,
                            },
                        });
                    }
                    this.intertextualPassages = intertextualPassages;
                    this.$bvModal.show("text-reuse");
                });
        },
        reUseTab() {
            if (this.pairid) {
                this.direction = null;
            }
            this.updateTocButton("ReuseTabs");
        },
        toggleDirection() {
            this.reload = true;
            this.$router.push(
                `/navigate/${this.philoDb}/${this.$route.params.doc}?intertextual=true&direction=${this.direction}`
            );
        },
        updateInit() {
            let firstPassage = document.querySelector(".passage-marker");
            let wordHighlight = document.querySelector(".highlight");
            if (!this.alreadyScrolled && firstPassage != null) {
                this.$nextTick(() => {
                    if (this.pairid) {
                        this.$scrollTo(document.querySelector(".passage-marker"), 1000, {
                            easing: "ease-out",
                            offset: -150,
                        });
                    }
                    let passageMarkers = document.getElementsByClassName("passage-marker");

                    Array.from(passageMarkers).forEach((el) => this.showPassage(el));
                    this.tippyInstances = [];
                    for (let i = 0; i < passageMarkers.length; i += 1) {
                        let passage = `.passage-${i}`;
                        let tippyInstances = tippy(passage, {
                            content() {
                                let popup = document.getElementById(`intertextual-metadata-${i}`);
                                return popup.innerHTML;
                            },
                            allowHTML: true,
                            maxWidth: 550,
                            theme: "light-border",
                            animation: "scale",
                        });
                        this.tippyInstances.push(...tippyInstances);
                    }
                });
                this.alreadyScrolled = true;
            } else if (wordHighlight && !this.alreadyScrolled) {
                this.$nextTick(() => {
                    this.$scrollTo(wordHighlight, 1000, {
                        easing: "ease-out",
                        offset: -150,
                    });
                    this.alreadyScrolled = true;
                });
            }
        },
        updateTocButton() {
            this.$nextTick(() => {
                let tocButton = document.querySelector("#show-toc");
                if (tocButton != null) {
                    this.navButtonPosition = tocButton.getBoundingClientRect().top;
                    if (this.navButtonPosition < 580) {
                        this.navButtonPosition = 580;
                    }
                }
            });
        },
        insertPageLinks(imgObj) {
            let currentObjImgs = imgObj.current_obj_img;
            let allImgs = imgObj.all_imgs;
            this.beforeObjImgs = [];
            this.afterObjImgs = [];
            if (currentObjImgs.length > 0) {
                let beforeIndex = 0;
                for (let i = 0; i < allImgs.length; i++) {
                    let img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.beforeObjImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.beforeObjImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                            ]);
                        }
                    } else {
                        beforeIndex = i;
                        break;
                    }
                }
                for (let i = beforeIndex; i < allImgs.length; i++) {
                    let img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.afterObjImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.afterObjImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                            ]);
                        }
                    }
                }
            }
        },
        insertInlineImgs(imgObj) {
            var currentObjImgs = imgObj.current_graphic_img;
            var allImgs = imgObj.graphics;
            var img;
            this.beforeGraphicsImgs = [];
            this.afterGraphicsImgs = [];
            if (currentObjImgs.length > 0) {
                var beforeIndex = 0;
                for (let i = 0; i < allImgs.length; i++) {
                    img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.beforeGraphicsImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.beforeGraphicsImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                            ]);
                        }
                    } else {
                        beforeIndex = i;
                        break;
                    }
                }
                for (let i = beforeIndex; i < allImgs.length; i++) {
                    img = allImgs[i];
                    if (currentObjImgs.indexOf(img[0]) === -1) {
                        if (img.length == 2) {
                            this.afterGraphicsImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[1]}`,
                            ]);
                        } else {
                            this.afterGraphicsImgs.push([
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                                `${this.$appConfig.philoDBs[this.philoDb].page_images_url_root}/${img[0]}`,
                            ]);
                        }
                    }
                }
            }
        },
        fetchToC() {
            this.tocPosition = "";
            var philoId = this.$route.params.doc.split("/").join(" ").trim();
            let docId = philoId.split(" ")[0];
            this.currentPhiloId = philoId;
            if (docId !== this.tocElements.docId) {
                this.$http
                    .get(`${this.philoUrl}/scripts/get_table_of_contents.py`, {
                        params: {
                            philo_id: this.currentPhiloId,
                        },
                    })
                    .then((response) => {
                        let tocElements = response.data.toc;
                        this.start = response.data.current_obj_position - 100;
                        if (this.start < 0) {
                            this.start = 0;
                        }
                        this.end = response.data.current_obj_position + 100;
                        this.tocElements = {
                            docId: philoId.split(" ")[0],
                            elements: tocElements,
                            start: this.start,
                            end: this.end,
                        };
                        let tocButton = document.querySelector("#show-toc");
                        tocButton.removeAttribute("disabled");
                        tocButton.classList.remove("disabled");
                        this.updateTocButton("fetchToC");
                    })
                    .catch((error) => {
                        console.log(error);
                    });
            } else {
                this.start = this.tocElements.start;
                this.end = this.tocElements.end;
                this.$nextTick(function () {
                    let tocButton = document.querySelector("#show-toc");
                    tocButton.removeAttribute("disabled");
                    tocButton.classList.remove("disabled");
                });
            }
        },
        setUpGallery() {
            // Image Gallery handling
            for (let imageType of ["page-image-link", "inline-img", "external-img"]) {
                Array.from(document.getElementsByClassName(imageType)).forEach((item) => {
                    item.addEventListener("click", (event) => {
                        event.preventDefault();
                        let target = event.srcElement;
                        this.gallery = Gallery(
                            [...document.getElementsByClassName(imageType)].map(
                                (item) => item.getAttribute("href") || item.getAttribute("src")
                            ),
                            {
                                index: Array.from(document.getElementsByClassName(imageType)).indexOf(target),
                                continuous: false,
                                thumbnailIndicators: false,
                            }
                        );
                    });
                });
                document.getElementById("full-size-image").addEventListener("click", () => {
                    let imageIndex = this.gallery.getIndex();
                    let img = Array.from(document.getElementsByClassName(imageType))[imageIndex].getAttribute(
                        "large-img"
                    );
                    window.open(img);
                });
            }
        },
        loadBefore() {
            var firstElement = this.tocElements[this.start - 2].philo_id;
            this.start -= 200;
            if (this.start < 0) {
                this.start = 0;
            }
            this.tocPosition = firstElement;
        },
        loadAfter() {
            this.end += 200;
        },
        toggleTableOfContents() {
            if (this.tocOpen) {
                this.tocOpen = false;
            } else {
                this.tocOpen = true;
                this.$nextTick(() => {
                    this.$scrollTo(document.querySelector(".current-obj"), 500, {
                        container: document.querySelector("#toc-content"),
                    });
                });
            }
        },
        backToTop() {
            window.scrollTo({ top: 0, behavior: "smooth" });
        },
        goToTextObject(philoID) {
            philoID = philoID.split(/[- ]/).join("/");
            if (this.tocOpen) {
                this.tocOpen = false;
            }
            this.$router.push({
                path: `/navigate/${this.philoDb}/${philoID}`,
                params: {},
            });
        },
        textObjectSelection(philoId, index) {
            event.preventDefault();
            let newStart = this.tocElements.start + index - 100;
            if (newStart < 0) {
                newStart = 0;
            }
            this.tocElements = {
                ...this.tocElements,
                start: newStart,
                end: this.tocElements.end - index + 100,
            };
            this.goToTextObject(philoId);
        },
        setUpNavBar() {
            let prevButton = document.querySelector("#prev-obj");
            let nextButton = document.querySelector("#next-obj");
            if (!this.next) {
                nextButton.classList.add("disabled");
            } else {
                nextButton.removeAttribute("disabled");
                nextButton.classList.remove("disabled");
            }
            if (!this.prev) {
                prevButton.classList.add("disabled");
            } else {
                prevButton.removeAttribute("disabled");
                prevButton.classList.remove("disabled");
            }
        },
        handleScroll() {
            if (!this.navBarVisible) {
                if (window.scrollY > this.navButtonPosition) {
                    this.navBarVisible = true;
                    let topBar = document.getElementById("toc-top-bar");
                    topBar.style.top = 0;
                    topBar.classList.add("visible", "shadow");
                    let tocWrapper = document.getElementById("toc-wrapper");
                    tocWrapper.style.top = "31px";
                    let navButtons = document.getElementById("nav-buttons");
                    navButtons.classList.add("visible");
                    let backToTop = document.getElementById("back-to-top");
                    backToTop.classList.add("visible");
                    let reportError = document.getElementById("report-error");
                    if (reportError != null) {
                        reportError.classList.add("visible");
                    }
                }
            } else if (window.scrollY < this.navButtonPosition) {
                this.navBarVisible = false;
                let topBar = document.getElementById("toc-top-bar");
                topBar.style.top = "initial";
                topBar.classList.remove("visible", "shadow");
                let tocWrapper = document.getElementById("toc-wrapper");
                tocWrapper.style.top = "0px";
                let navButtons = document.getElementById("nav-buttons");
                navButtons.style.top = "initial";
                navButtons.classList.remove("visible");
                let backToTop = document.getElementById("back-to-top");
                backToTop.classList.remove("visible");
                let reportError = document.getElementById("report-error");
                if (reportError != null) {
                    reportError.classList.remove("visible");
                }
            }
        },
        lookUp(event, value) {
            let selection = window.getSelection().toString();
            if (event.key === "d") {
                let year = value[`${this.dbPrefix}date`].split("-")[0];
                let century = parseInt(year.slice(0, year.length - 2));
                let range = `${century.toString()}00-${String(century + 1)}00`;
                console.log(selection, century, range);
                if (range == "NaN00-NaN00") {
                    range = "";
                }
                let link = `https://artflsrv03.uchicago.edu/cgi-bin/quickdict.pl?docyear=${range}&strippedhw=${selection}`;
                window.open(link);
            } else if (event.key == "s") {
                this.$http
                    .post(`${this.$appConfig.apiServer}/intertextual-hub-api/submit_passage`, {
                        passage: selection,
                    })
                    .then((response) => {
                        this.passageSimilarDocs = response.data;
                        this.$bvModal.show("similar-docs");
                    });
            }
        },
        toggleSimDocs() {
            this.showAllSimDocs = true;
            this.updateTocButton("toggleSimDocs");
        },
        showHeads(docIndex) {
            document.querySelector(`#reuse-${docIndex} ul`).style.display = "block";
        },
        goToPassage(passageid) {
            let n = 0;
            outerLoop: for (let passageGroup of this.intertextualMetadata) {
                for (let passage of passageGroup) {
                    if (passage.passageid == passageid) {
                        break outerLoop;
                    }
                }
                n += 1;
            }
            this.$scrollTo(document.querySelector(`.passage-marker[n='${n}']`), 1000, {
                easing: "ease-out",
                offset: -150,
                onDone: () => {
                    this.$nextTick(() => {
                        document.querySelectorAll(`.passage-${n}`).forEach((el) => {
                            el.classList.add("color-change");
                            setTimeout(() => {
                                el.classList.remove("color-change");
                            }, 500);
                        });
                    }, 1000);
                },
            });
        },
    },
};
</script>
<style scoped lang="scss">
@import "../assets/theme.scss";
@import "~bootstrap/scss/bootstrap.scss";
@import "~bootstrap-vue/src/index.scss";

.toc-div1 > a,
.toc-div2 > a,
.toc-div3 > a {
    padding: 5px 5px 5px 0px;
}
.bullet-point-div1,
.bullet-point-div2,
.bullet-point-div3 {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
}
.bullet-point-div1 {
    border: solid 1px;
}
.bullet-point-div2 {
    border: solid 2px;
}
.bullet-point-div3 {
    border: solid 1px;
}
.toc-div1,
.toc-div2,
.toc-div3 {
    text-indent: -0.9em;
    /*Account for the bullet point*/
    margin-bottom: 5px;
}
.toc-div1 {
    padding-left: 0.9em;
}
.toc-div2 {
    padding-left: 1.9em;
}
.toc-div3 {
    padding-left: 2.9em;
}
.toc-div1:hover,
.toc-div2:hover,
.toc-div3:hover {
    cursor: pointer;
}
::v-deep .nav-tabs {
    border-bottom-width: 0;
}
::v-deep .nav-link {
    background-color: rgba(143, 57, 49, 0.8);
    border-color: rgba(143, 57, 49, 0.8);
    border-bottom: 1px solid #dee2e6;
    color: #fff;
    transition: all 250ms;
}

::v-deep .nav-link.active {
    color: $link-color;
    border-bottom-color: transparent !important;
    background-color: #fff;
}
.separator {
    padding: 5px;
    font-size: 60%;
    display: inline-block;
    vertical-align: middle;
}
#toc-content {
    display: inline-block;
    position: relative;
    max-height: 30vh;
    overflow: scroll;
    text-align: justify;
    line-height: 180%;
    z-index: 50;
    background: #fff;
}
#toc-wrapper {
    position: relative;
    z-index: 49;
    pointer-events: all;
}
#toc-top-bar {
    height: 31px;
    width: 100%;
    left: 0;
    pointer-events: none;
}
#toc {
    margin-top: 31px;
    pointer-events: all;
}
#toc-top-bar.visible {
    position: fixed;
}
#nav-buttons.visible {
    position: fixed;
    backdrop-filter: blur(0.5rem);
    background-color: rgba(255, 255, 255, 0.3);
    pointer-events: all;
}
#back-to-top.visible {
    opacity: 1;
    pointer-events: all;
}
#nav-buttons {
    position: absolute;
    opacity: 0.9;
    width: 100%;
}
#toc-nav-bar {
    background-color: #ddd;
    opacity: 0.95;
    backdrop-filter: blur(5px) contrast(0.8);
}
a.current-obj,
#toc-container a:hover {
    background: #e8e8e8;
}
#back-to-top {
    position: absolute;
    left: 0;
    opacity: 0;
    transition: opacity 0.25s;
    pointer-events: none;
}
#direction-toggle {
    display: inline-block;
    padding: 0.5rem;
}
#direction-toggle fieldset {
    margin-bottom: 0;
}
#intertextual-metadata {
    background-color: white;
}
::v-deep [class*="passage-"] {
    color: indianred;
    background-color: white;
    transition: all 500ms ease;
}
::v-deep [class*="passage-"]:hover {
    cursor: pointer;
}
::v-deep .color-change {
    background-color: indianred;
    color: #fff;
}
::v-deep .passage-marker {
    display: inline-block;
    margin: 0 0.15rem;
    font-weight: 700;
    font-style: normal;
}
::v-deep .passage-marker:hover {
    background-color: #a74b4b;
    opacity: initial;

    cursor: pointer;
}
::v-deep .intertextual-link {
    display: inline-block;
    margin: 0 0.25rem;
    padding: 0 0.25rem;
    cursor: pointer;
    background-color: dodgerblue;
    color: white;
}
::v-deep .xml-pb {
    display: block;
    text-align: center;
    margin: 10px;
}
::v-deep .xml-pb::before {
    content: "-" attr(n) "-";
    white-space: pre;
}
::v-deep p {
    margin-bottom: 0.5rem;
}
::v-deep .highlight {
    background-color: indianred;
    color: #fff;
}
/* Styling for theater */
::v-deep .xml-castitem::after {
    content: "\A";
    white-space: pre;
}
::v-deep .xml-castlist > .xml-castitem:first-of-type::before {
    content: "\A";
    white-space: pre;
}
::v-deep .xml-castgroup::before {
    content: "\A";
    white-space: pre;
}
b.headword {
    font-weight: 700 !important;
    font-size: 130%;
    display: block;
    margin-top: 20px;
}
::v-deep #bibliographic-results b.headword {
    font-weight: 400 !important;
    font-size: 100%;
    display: inline;
}
::v-deep .xml-lb,
::v-deep .xml-l {
    text-align: justify;
    display: block;
}
::v-deep .xml-sp .xml-lb:first-of-type {
    content: "";
    white-space: normal;
}
::v-deep .xml-lb[type="hyphenInWord"] {
    display: inline;
}
#book-page .xml-sp {
    display: block;
}
::v-deep .xml-sp::before {
    content: "\A";
    white-space: pre;
}
::v-deep .xml-stage + .xml-sp:nth-of-type(n + 2)::before {
    content: "";
}
::v-deep .xml-fw,
::v-deep .xml-join {
    display: none;
}
::v-deep .xml-speaker + .xml-stage::before {
    content: "";
    white-space: normal;
}
::v-deep .xml-stage {
    font-style: italic;
}
::v-deep .xml-stage::after {
    content: "\A";
    white-space: pre;
}
::v-deep div1 div2::before {
    content: "\A";
    white-space: pre;
}
::v-deep .xml-speaker {
    font-weight: 700;
}
::v-deep .xml-pb {
    display: block;
    text-align: center;
    margin: 10px;
}
::v-deep .xml-pb::before {
    content: "-" attr(n) "-";
    white-space: pre;
}
::v-deep .xml-lg {
    display: block;
}
::v-deep .xml-lg::after {
    content: "\A";
    white-space: pre;
}
::v-deep .xml-lg:first-of-type::before {
    content: "\A";
    white-space: pre;
}
::v-deep .xml-castList,
::v-deep .xml-front,
::v-deep .xml-castItem,
::v-deep .xml-docTitle,
::v-deep .xml-docImprint,
::v-deep .xml-performance,
::v-deep .xml-docAuthor,
::v-deep .xml-docDate,
::v-deep .xml-premiere,
::v-deep .xml-casting,
::v-deep .xml-recette,
::v-deep .xml-nombre {
    display: block;
}
::v-deep .xml-docTitle {
    font-style: italic;
    font-weight: bold;
}
::v-deep .xml-docTitle,
::v-deep .xml-docAuthor,
::v-deep .xml-docDate {
    text-align: center;
}
::v-deep .xml-docTitle span[type="main"] {
    font-size: 150%;
    display: block;
}
::v-deep .xml-docTitle span[type="sub"] {
    font-size: 120%;
    display: block;
}
::v-deep .xml-performance,
::v-deep .xml-docImprint {
    margin-top: 10px;
}
::v-deep .xml-set {
    display: block;
    font-style: italic;
    margin-top: 10px;
}
/*Dictionary formatting*/
body {
    counter-reset: section;
    /* Set the section counter to 0 */
}
::v-deep .xml-prononciation::before {
    content: "(";
}
::v-deep .xml-prononciation::after {
    content: ")\A";
}
::v-deep .xml-nature {
    font-style: italic;
}
::v-deep .xml-indent,
::v-deep .xml-variante {
    display: block;
}
::v-deep .xml-variante {
    padding-top: 10px;
    padding-bottom: 10px;
    text-indent: -1.3em;
    padding-left: 1.3em;
}
::v-deep .xml-variante::before {
    counter-increment: section;
    content: counter(section) ")\00a0";
    font-weight: 700;
}
::v-deep :not(.xml-rubrique) + .xml-indent {
    padding-top: 10px;
}
::v-deep .xml-indent {
    padding-left: 1.3em;
}
::v-deep .xml-cit {
    padding-left: 2.3em;
    display: block;
    text-indent: -1.3em;
}
::v-deep .xml-indent > .xml-cit {
    padding-left: 1em;
}
::v-deep .xml-cit::before {
    content: "\2012\00a0\00ab\00a0";
}
::v-deep .xml-cit::after {
    content: "\00a0\00bb\00a0("attr(aut) "\00a0"attr(ref) ")";
    font-variant: small-caps;
}
::v-deep .xml-rubrique {
    display: block;
    margin-top: 20px;
}
::v-deep .xml-rubrique::before {
    content: attr(nom);
    font-variant: small-caps;
    font-weight: 700;
}
::v-deep .xml-corps + .xml-rubrique {
    margin-top: 10px;
}
/*Methodique styling*/
::v-deep div[type="article"] .headword {
    display: inline-block;
    margin-bottom: 10px;
}
::v-deep .headword + p {
    display: inline;
}
::v-deep .headword + p + p {
    margin-top: 10px;
}
/*Note handling*/
::v-deep .popover {
    max-width: 350px;
    overflow: scroll;
}
::v-deep .popover-content {
    text-align: justify;
}
::v-deep .popover-content .xml-p:not(:first-of-type) {
    display: block;
    margin-top: 1em;
    margin-bottom: 1em;
}
::v-deep .note-content {
    display: none;
}
::v-deep .note,
::v-deep .note-ref {
    vertical-align: 0.3em;
    font-size: 0.7em;
}
::v-deep .note:hover,
::v-deep .note-ref:hover {
    cursor: pointer;
    text-decoration: none;
}
::v-deep div[type="notes"] .xml-note {
    margin: 15px 0px;
    display: block;
}
::v-deep .xml-note::before {
    content: "note\00a0"attr(n) "\00a0:\00a0";
    font-weight: 700;
}
/*Page images*/
::v-deep .xml-pb-image {
    display: block;
    text-align: center;
    margin: 10px;
}
::v-deep .page-image-link {
    margin-top: 10px;
    /*display: block;*/
    text-align: center;
}
/*Inline images*/
::v-deep .inline-img {
    max-width: 40%;
    float: right;
    height: auto;
    padding-left: 15px;
    padding-top: 15px;
}
::v-deep .inline-img:hover {
    cursor: pointer;
}
::v-deep .link-back {
    margin-left: 10px;
    line-height: initial;
}
::v-deep .xml-add:after {
    content: "[Passage by " attr(resp) "]";
    visibility: visible;
    text-transform: capitalize;
    font-variant: small-caps;
    font-size: 90%;
}
::v-deep .xml-add {
    color: #3fa673;
}
::v-deep .xml-seg {
    display: block;
}
/*Table display*/
::v-deep b.headword[rend="center"] {
    margin-bottom: 30px;
    text-align: center;
}
::v-deep .xml-table {
    display: table;
    position: relative;
    text-align: center;
    border-collapse: collapse;
}
::v-deep .xml-table .xml-pb-image {
    position: absolute;
    width: 100%;
    margin-top: 15px;
}
::v-deep .xml-row {
    display: table-row;
    font-weight: 700;
    text-align: left;
    min-height: 50px;
    font-variant: small-caps;
    padding-top: 10px;
    padding-bottom: 10px;
    padding-right: 20px;
    border-bottom: #ddd 1px solid;
}
::v-deep .xml-row ~ .xml-row {
    font-weight: inherit;
    text-align: justify;
    font-variant: inherit;
}
::v-deep .xml-pb-image + .xml-row {
    padding-top: 50px;
    padding-bottom: 10px;
    border-top-width: 0px;
}
::v-deep .xml-cell {
    display: table-cell;
    padding-top: inherit; /*inherit padding when image is above */
    padding-bottom: inherit;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
    transform: translateY(-30px);
    opacity: 0;
}

/* Image button styling */
.img-buttons {
    font-size: 45px !important;
    color: #fff !important;
    /* background-image: initial; */
}
#full-size-image {
    right: 90px;
    font-weight: 700 !important;
    font-size: 20px !important;
    left: auto;
    margin: -15px;
    text-decoration: none;
    cursor: pointer;
    position: absolute;
    top: 28px;
    color: #fff;
    opacity: 0.8;
    border: 3px solid;
    padding: 0 0.25rem;
}
#full-size-image:hover {
    opacity: 1;
}
.docs-cited,
.docs-cited-heads {
    cursor: pointer;
    color: $link-color;
}
</style>
