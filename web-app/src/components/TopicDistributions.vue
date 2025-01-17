<template>
    <b-container fluid style="background-color: #fff">
        <div class="mb-4">
            <b-table
                hover
                :items="sortedTopicDistribution"
                :fields="fields"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
                @row-clicked="goToTopic"
            >
                <template v-slot:cell(name)="data">
                    <span
                        class="frequency-parent d-inline-block"
                        style="min-width: 80px"
                        >Topic {{ data.value }}</span
                    >
                </template>
                <template v-slot:cell(description)="data">
                    <span class="frequency-parent">{{ data.value }}</span>
                </template>
                <template v-slot:cell(frequency)="data">
                    <span class="d-inline-block" style="min-width: 230px">
                        <span class="frequency-value pl-2"
                            >{{
                                (data.value.toFixed(8) * 100).toFixed(4)
                            }}%</span
                        >
                        <span
                            class="frequency-bar"
                            :style="`width: ${
                                data.value * frequencyMultiplier
                            }%; max-height: 3em`"
                        ></span>
                    </span>
                </template>
            </b-table>
        </div>
    </b-container>
</template>

<script>
export default {
    name: "TopicDistributions",
    data() {
        return {
            routeName: this.$route.name,
            localTopics: this.$topicModelData.topics_words,
        };
    },
    mounted() {
        document
            .querySelectorAll("tr > td:nth-child(3)")
            .forEach(function (element) {
                element.style.position = "relative";
                element.style.padding = "0.75rem";
            });
    },
    computed: {
        fields: function () {
            let fields = [
                { key: "name", label: "Topic", sortable: true },
                { key: "description", label: "Top 10 tokens", sortable: false },
                {
                    key: "frequency",
                    label: "Importance across collections",
                    sortable: true,
                },
            ];
            return fields;
        },
        sortBy: {
            get: function () {
                if (this.$route.name == "home") {
                    return "name";
                } else {
                    return "frequency";
                }
            },
            set: (value) => {
                return value;
            },
        },
        sortDesc: {
            get: function () {
                if (this.$route.name == "home") {
                    return false;
                } else {
                    return true;
                }
            },
            set: (value) => {
                return value;
            },
        },
        frequencyMultiplier() {
            let maxFrequency = 0.0;
            for (let topic of this.localTopics) {
                if (topic.frequency > maxFrequency) {
                    maxFrequency = topic.frequency;
                }
            }
            return 100 / maxFrequency;
        },
        fieldValue() {
            if (this.$route.name == "home") {
                return "the corpus";
            } else {
                return `${this.$route.params.fieldValue}`;
            }
        },
        sortedTopicDistribution() {
            let topicsWithDescription = [];
            for (let topicName in this.localTopics) {
                topicsWithDescription.push({
                    name: `${topicName}`,
                    description: this.localTopics[topicName].description,
                    frequency: this.localTopics[topicName].frequency,
                });
            }
            return topicsWithDescription;
        },
    },
    methods: {
        goToTopic(topic) {
            this.$router.push(`/topic/${topic.name}`);
        },
    },
};
</script>

<style lang="scss" scoped>
@import "../assets/theme.scss";
@import "~bootstrap/scss/bootstrap.scss";
@import "~bootstrap-vue/src/index.scss";
.frequency-value {
    display: inline-block;
    position: relative;
    z-index: 1;
    color: $link-color;
}
.frequency-bar {
    display: inline-block;
    position: absolute;
    left: 0;
    top: 0;
    padding: 0.75rem;
    height: 100%;
    background-color: $yellow;
    background-clip: content-box;
}
::v-deep td {
    cursor: pointer;
    position: relative;
}
</style>
