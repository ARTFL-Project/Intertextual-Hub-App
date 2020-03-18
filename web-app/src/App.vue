<template>
    <div id="app">
        <b-navbar type="light" variant="light" class="shadow">
            <b-navbar-nav>
                <b-navbar-brand>Intertextual Hub</b-navbar-brand>
            </b-navbar-nav>
        </b-navbar>
        <b-container fluid class="mt-4"
            ><search-form></search-form>
        </b-container>
    </div>
</template>

<script>
import SearchForm from "./components/SearchForm.vue";

export default {
    name: "App",
    components: {
        SearchForm
    },
    data() {
        return {};
    }
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
#intertextual-metadata {
    background-color: white;
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
    background-color: red;
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
::v-deep .xml-add {
    color: #ef4500;
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
</style>
