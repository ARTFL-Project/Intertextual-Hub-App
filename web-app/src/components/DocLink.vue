<template>
    <b-popover :target="`${target}`" triggers="focus" placement="top">
        <template v-slot:title>
            <span style="font-variant: small-caps;">Choose between:</span>
        </template>
        <b-list-group flush>
            <b-list-group-item class="px-1 py-2">
                <router-link :to="philoLink">Read document</router-link>
            </b-list-group-item>
            <b-list-group-item class="px-1 py-2">
                Read document with reuses:
                <br />-
                <router-link :to="`${navLink}&direction=target`">from earlier texts</router-link>
                <br />-
                <router-link :to="`${navLink}&direction=source`">from later texts</router-link>
            </b-list-group-item>
            <b-list-group-item class="px-1 py-2">
                <router-link :to="`${topicLink}`">Explore topic distribution</router-link>
            </b-list-group-item>
        </b-list-group>
    </b-popover>
</template>
<script>
export default {
    name: "DocLink",
    props: ["philoDb", "target", "philoId"],
    data() {
        return {
            philoUrl: this.$appConfig.philoDBs[this.philoDb].url,
            philoType: this.$appConfig.philoDBs[this.philoDb].object_type,
        };
    },
    computed: {
        objectId: function () {
            if (this.philoType == "doc") {
                return this.philoId.split(" ")[0];
            } else if (this.philoType == "div1") {
                return this.philoId.split(" ").slice(0, 2).join("/");
            }
            return this.philoId.split(" ").slice(0, 3).join("/");
        },
        philoLink: function () {
            return `/navigate/${this.philoDb}/${this.objectId}`;
        },
        topicLink: function () {
            return `/document/${this.philoDb}/${this.objectId}/`;
        },
        navLink: function () {
            return `/navigate/${this.philoDb}/${this.objectId}?intertextual=true`;
        },
    },
};
</script>