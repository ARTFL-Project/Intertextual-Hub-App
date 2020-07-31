<template>
    <b-popover :target="`${target}`" triggers="click blur" placement="top">
        <template v-slot:title>
            <span style="font-variant: small-caps;">{{ word }}</span>
        </template>
        <b-list-group flush>
            <b-list-group-item>
                <router-link :to="`/word/${word}`">Explore usage in corpus</router-link>
            </b-list-group-item>
            <b-list-group-item>
                <a :href="link" v-if="metadata">See all occurrences in document</a>
                <a :href="`/search?words=${word}`" v-else>See all occurrences</a>
            </b-list-group-item>
        </b-list-group>
    </b-popover>
</template>
<script>
export default {
    name: "WordLink",
    props: ["target", "metadata", "word"],
    data() {
        return {
            philoUrl: this.$appConfig.philoDBs[this.metadata.philo_db].url,
        };
    },
    computed: {
        link: function () {
            let params = { q: this.word };
            if (this.metadata.author.length) {
                params.author = `"${this.metadata.author}"`;
            }
            if (this.metadata.title.length) {
                params.title = `"${this.metadata.title}"`;
            }
            if (this.metadata.head.length) {
                params.head = `"${this.metadata.head}"`;
            }
            if (this.metadata.philo_type == "doc") {
                return `${
                    this.philoUrl
                }/query?report=concordance&${this.paramsToUrlString(params)}`;
            }
            return `${
                this.philoUrl
            }/query?report=concordance&${this.paramsToUrlString(params)}`;
        },
    },
};
</script>
