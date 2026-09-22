<script>
import { EventBus } from "../main.js";

export default {
    name: "RenderString",
    props: {
        string: {
            required: true,
            type: String
        }
    },
    render(h) {
        const render = {
            template: "<div>" + this.string + "</div>",
            data: () => ({
                framework: "Vue"
            }),
            created() {
                this.$nextTick(() => {
                    document
                        .getElementsByClassName("bi-flag-fill")
                        .forEach(el =>
                            el.addEventListener("click", () => {
                                let passageNumber = el.getAttribute("n");
                                let offsets = el.dataset.offsets.split("-");
                                EventBus.$emit("showPassage", {
                                    offsets: offsets,
                                    passageNumber: passageNumber,
                                    element: el
                                });
                            })
                        );
                });
            }
        };
        return h(render);
    }
};
</script>
<style scoped>
::v-deep .bi-flag-fill {
    border: 1px solid royalblue;
    color: royalblue;
    background-color: white;
    margin: 0 0.25rem;
    border-radius: 50%;
    height: 1.25rem;
    width: 1.25rem;
    padding: 0.1rem;
}
::v-deep .bi-flag-fill:hover {
    border: 1px solid white;
    color: white;
    background-color: royalblue;
    cursor: pointer;
}
</style>
