<template>
    <b-row>
        <b-col cols="6" class="mt-2">
            <h6 class="text-center pb-2">Earlier Use</h6>
            <p class="pt-3 px-3">
                {{ passage.source_author }}
                <span class="separator">&#9679;</span>
                <i>{{ passage.source_title }}</i>
                <span class="separator">&#9679;</span>
                <span v-if="passage.source_year">{{ passage.source_year }}</span>
            </p>
        </b-col>
        <b-col cols="6" class="mt-2 border border-top-0 border-right-0 border-bottom-0">
            <h6 class="text-center pb-2">Later use</h6>
            <p class="pt-3 px-3">
                {{ passage.target_author }}
                <span class="separator">&#9679;</span>
                <i>{{ passage.target_title }}</i>
                <span class="separator">&#9679;</span>
                <span v-if="passage.target_year">{{ passage.target_year }}</span>
            </p>
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
export default {
    name: "PassagePair",
    props: ["passage"]
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