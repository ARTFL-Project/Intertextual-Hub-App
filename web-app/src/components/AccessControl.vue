<template>
    <b-container fluid>
        <div id="access-control-container" class="mt-4">
            <b-card
                class="text-center mt-4 shadow"
                title="Access Restricted by our data use agreement"
                title-tag="h3"
                sub-title="If you wish to gain access to this ressource, please get
                        in touch by email at artfl@artfl.uchicago.edu"
            >
                <b-form
                    @submit.prevent
                    @reset="reset()"
                    @keyup.enter="submit()"
                    id="password-access"
                    class="mt-4 p-4"
                    style="text-align: justify"
                >
                    <h5 v-if="!accessDenied" class="mt-2 mb-3">
                        If you have a username and password, please enter them
                        here:
                    </h5>
                    <h5 class="text-danger" v-if="accessDenied">
                        Your username or password don't match. Please try again.
                    </h5>
                    <b-row class="mb-3">
                        <b-col cols="12" sm="6" md="5" lg="4">
                            <b-input-group prepend="Username">
                                <b-form-input
                                    v-model="accessInput.username"
                                ></b-form-input>
                            </b-input-group>
                        </b-col>
                    </b-row>
                    <b-row class="mb-3">
                        <b-col cols="12" sm="6" md="5" lg="4">
                            <b-input-group prepend="Password">
                                <b-form-input
                                    v-model="accessInput.password"
                                ></b-form-input>
                            </b-input-group>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col cols="12">
                            <b-button-group>
                                <b-button @click="submit">Submit</b-button>
                                <b-button
                                    type="reset"
                                    variant="danger"
                                    @click="reset"
                                    >Reset</b-button
                                >
                            </b-button-group>
                        </b-col>
                    </b-row>
                </b-form>
            </b-card>
        </div>
    </b-container>
</template>
<script>
// import { EventBus } from "../main.js";
export default {
    name: "AccessControl",
    props: ["authorized", "clientIp", "domainName"],
    data() {
        return {
            accessInput: { username: "", password: "" },
            accessDenied: false,
        };
    },
    created() {},
    methods: {
        submit() {
            this.$http
                .post(
                    `${this.$appConfig.apiServer}/intertextual-hub-api/login`,
                    {
                        username: this.accessInput.username,
                        password: this.accessInput.password,
                    }
                )
                .then((response) => {
                    if (response.data) {
                        location.reload();
                    } else {
                        this.accessDenied = true;
                    }
                });
        },
        reset() {
            this.accessInput = { username: "", password: "" };
        },
    },
};
</script>