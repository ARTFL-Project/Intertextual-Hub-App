<template>
    <span class="d-inline-block">
        <a class="word-link" :id="target" href="" @click.prevent>{{ word }}</a>
        <b-popover :target="`${target}`" triggers="focus" placement="top">
            <template v-slot:title>
                <span style="font-variant: small-caps">{{ word }}</span>
            </template>
            <b-list-group flush>
                <b-list-group-item v-if="extraLink">
                    <router-link :to="extraLink.link" v-html="extraLink.text"></router-link>
                </b-list-group-item>
                <b-list-group-item>
                    <router-link :to="`/word/${word}`">Explore usage in corpus</router-link>
                </b-list-group-item>
                <b-list-group-item>
                    <a :href="link" target="_blank" v-if="metadata && philoUrl">See all occurrences in document</a>
                    <router-link :to="`/search?words=${word}`" v-else>Find most relevant documents</router-link>
                </b-list-group-item>
            </b-list-group>
        </b-popover>
    </span>
</template>
<script>
export default {
    name: "WordLink",
    props: ["target", "metadata", "word", "extraLink"],
    data() {
        return {
            philoUrl: null,
        };
    },
    created() {
        if (this.metadata) {
            this.philoUrl = this.$appConfig.philoDBs[this.metadata.philo_db].url;
        }
    },
    computed: {
        link: function () {
            let params = { q: `${this.word}.*` };
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
                return `${this.philoUrl}/query?report=concordance&${this.paramsToUrlString(params)}`;
            }
            return `${this.philoUrl}/query?report=concordance&${this.paramsToUrlString(params)}`;
        },
    },
};
</script>
<style lang="scss" scoped>
@import "../assets/theme.scss";
@import "~bootstrap/scss/bootstrap.scss";
@import "~bootstrap-vue/src/index.scss";
.word-link {
    color: $link-color;
    cursor: pointer;
    display: inline-block;
    text-decoration: none;
}
</style>