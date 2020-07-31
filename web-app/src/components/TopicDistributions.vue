<template>
    <b-container fluid class="mt-4">
        <b-card no-body class="shadow-sm mb-4">
            <h6 slot="header" class="mb-0 text-center">
                Topics and their relative distribution in corpus
            </h6>
            <b-table
                hover
                :items="sortedTopicDistribution"
                :fields="fields"
                :sort-by.sync="sortBy"
                :sort-desc.sync="sortDesc"
                @row-clicked="goToTopic"
            >
                <template v-slot:cell(name)="data">
                    <span class="frequency-parent">Topic {{ data.value }}</span>
                </template>
                <template v-slot:cell(description)="data">
                    <span class="frequency-parent">{{ data.value }}</span>
                </template>
                <template v-slot:cell(frequency)="data">
                    <span class="frequency-value pl-2"
                        >{{ (data.value.toFixed(8) * 100).toFixed(4) }}%</span
                    >
                    <span
                        class="frequency-bar"
                        :style="`width: ${data.value * frequencyMultiplier}%;`"
                    ></span>
                </template>
            </b-table>
        </b-card>
    </b-container>
</template>

<script>
export default {
    name: "TopicDistributions",
    data() {
        return {
            routeName: this.$route.name,
            localTopics: null,
        };
    },
    created() {
        this.$http
            .get(
                "https://anomander.uchicago.edu/topologic-api/get_config/combo?full_config=True"
            )
            .then((response) => {
                this.localTopics = response.data.topics_words;
            });
    },
    mounted() {
        document
            .querySelectorAll("tr > td:nth-child(3)")
            .forEach(function(element) {
                element.style.position = "relative";
                element.style.padding = "0.75rem";
            });
    },
    computed: {
        fields: function() {
            let fields = [
                { key: "name", label: "Topic", sortable: true },
                { key: "description", label: "Top 10 tokens", sortable: false },
                {
                    key: "frequency",
                    label: "Relative global weight across corpus",
                    sortable: true,
                },
            ];
            return fields;
        },
        sortBy: {
            get: function() {
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
            get: function() {
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

<style scoped>
.frequency-value {
    display: inline-block;
}
.frequency-bar {
    display: inline-block;
    position: absolute;
    left: 0;
    top: 0;
    padding: 0.75rem;
    height: 100%;
    background-color: rgba(85, 172, 238, 0.4);
    background-clip: content-box;
}
::v-deep td {
    cursor: pointer;
    position: relative;
}
</style>
