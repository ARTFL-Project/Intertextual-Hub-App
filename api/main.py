import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import aligner
import search
import similarity
from words import get_word_evolution, retrieve_associated_words
from typing import List, Optional, Dict


app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.mount("/css", StaticFiles(directory="../web-app/dist/intertextual-hub/css"), name="css")
app.mount("/js", StaticFiles(directory="../web-app/dist/intertextual-hub/js"), name="js")


with open("./db_config.json") as db_config_file:
    db_config = json.load(db_config_file)
    PHILO_URLS = {dbname: values["url"] for dbname, values in db_config["philo_dbs"].items()}

PHILO_TYPE = {1: "doc", 2: "div1", 3: "div2"}


@app.get("/")
@app.get("/navigate/{philo_db}/{doc}")
@app.get("/navigate/{philo_db}/{doc}/{div1}")
@app.get("/navigate/{philo_db}/{doc}/{div1}/{div2}")
@app.get("/navigate/{philo_db}/{doc}/{div1}/{div2}/{div3}")
@app.get("/navigate/{philo_db}/{doc}/{div1}/{div2}/{div3}/{para}")
@app.get("/navigate/{philo_db}/{doc}/{div1}/{div2}/{div3}/{para}/{sent}")
@app.get("/navigate/{philo_db}/{doc}/{div1}/{div2}/{div3}/{para}/{sent}/{word}")
@app.get("/seq-pair/search")
@app.get("/search")
@app.get("/topic/{topic}")
@app.get("/document/{db}/{doc}")
@app.get("/document/{db}/{doc}/{div1}")
@app.get("/document/{db}/{doc}/{div1}/{div2}")
@app.get("/document/{db}/{doc}/{div1}/{div2}/{div3}")
@app.get("/document/{db}/{doc}/{div1}/{div2}/{div3}/{para}")
@app.get("/document/{db}/{doc}/{div1}/{div2}/{div3}/{para}/{sent}")
@app.get("/document/{db}/{doc}/{div1}/{div2}/{div3}/{para}/{sent}/{word}")
@app.get("/word/{word}")
def home():
    with open("../web-app/dist/index.html") as html:
        index_html = html.read()
    return HTMLResponse(index_html)


@app.get("/get_text/{philo_db}")
def get_text(
    philo_db: str,
    philo_id: str,
    direction: Optional[str] = None,
    pairid: Optional[str] = None,
    intertextual: Optional[bool] = None,
    byte: Optional[str] = None,
):
    text_object_id: List[str] = philo_id.split()
    while text_object_id[-1] == "0":
        text_object_id.pop()
    text_object_type = PHILO_TYPE[len(text_object_id)]
    if pairid is not None:
        passage_data = aligner.get_passage_byte_offsets(pairid, direction)
        while text_object_id[-1] == "0":
            text_object_id.pop()
        philologic_response = requests.post(
            f"{PHILO_URLS[philo_db]}/reports/navigation.py",
            params={"philo_id": " ".join(text_object_id)},
            json={"passages": passage_data["passages"]},
        )
        philo_text_object = philologic_response.json()
        return {
            "text": philo_text_object["text"],
            "prev": philo_text_object["prev"],
            "next": philo_text_object["next"],
            "imgs": philo_text_object["imgs"],
            "intertextual_metadata": [[passage_data["metadata"]] for _ in passage_data["metadata"]["passages"]],
            "doc_metadata": {
                field: value for field, value in passage_data["metadata"].items() if field.startswith(direction)
            },
            "object_type": text_object_type,
        }
    elif intertextual is True:
        passage_data, metadata_list, doc_metadata, docs_cited = aligner.get_passage_by_philo_id(
            text_object_id, philo_db, direction=direction
        )
        if passage_data is None:
            philologic_response = requests.post(
                f"{PHILO_URLS[philo_db]}/reports/navigation.py", params={"philo_id": " ".join(text_object_id)},
            )
            philo_text_object = philologic_response.json()
            return {
                "text": philo_text_object["text"],
                "prev": philo_text_object["prev"],
                "next": philo_text_object["next"],
                "imgs": philo_text_object["imgs"],
                "doc_metadata": {
                    f"{direction}_philo_db": philo_db,
                    f"{direction}_philo_id": " ".join(text_object_id),
                    f"{direction}_date": philo_text_object["metadata_fields"]["year"],
                    **{f"{direction}_{field}": value for field, value in philo_text_object["metadata_fields"].items()},
                },
                "intertextual_metadata": [],
                "object_type": text_object_type,
            }
        philologic_response = requests.post(
            f"{PHILO_URLS[philo_db]}/reports/navigation.py",
            params={"philo_id": " ".join(text_object_id)},
            json={"passages": passage_data},
        )
        philo_text_object = philologic_response.json()
        return {
            "text": philo_text_object["text"],
            "prev": philo_text_object["prev"],
            "next": philo_text_object["next"],
            "imgs": philo_text_object["imgs"],
            "intertextual_metadata": metadata_list,
            "doc_metadata": doc_metadata,
            "docs_cited": docs_cited,
            "object_type": text_object_type,
        }
    else:
        philologic_response = requests.post(
            f"{PHILO_URLS[philo_db]}/reports/navigation.py",
            params={"philo_id": " ".join(text_object_id), "byte": byte},
        )
        philo_text_object = philologic_response.json()
        if direction is not None:
            prefix = f"{direction}_"
        else:
            prefix = ""
        return {
            "text": philo_text_object["text"],
            "prev": philo_text_object["prev"],
            "imgs": philo_text_object["imgs"],
            "next": philo_text_object["next"],
            "doc_metadata": {
                f"{prefix}philo_db": philo_db,
                f"{prefix}philo_id": " ".join(text_object_id),
                f"{prefix}date": philo_text_object["metadata_fields"]["year"],
                **{f"{prefix}{field}": value for field, value in philo_text_object["metadata_fields"].items()},
            },
            "intertextual_metadata": [],
            "object_type": text_object_type,
        }


@app.get("/search_alignments")
def search_alignments(request: Request):
    results = aligner.search_alignments(**request.query_params)
    return results


@app.get("/search_alignments2")
def search_alignments2(request: Request):
    results = aligner.search_alignments2(**request.query_params)
    return results[:50]


@app.get("/retrieve_passages/{pairid}")
def retrieve_passages(pairid: str):
    passages = aligner.get_passages(pairid)
    return passages


@app.get("/retrieve_passage/{pairid}")
def retrieve_passage(pairid: str, start_byte: int, direction: str):
    passage = aligner.get_passage(pairid, start_byte, direction)
    return passage


@app.post("/retrieve_passages_all/")
def retrieve_passages_all(passages: Dict[str, List[str]]):
    print(passages["pairids"])
    passage_objects = aligner.get_passages_by_pairids_and_passageids(passages["pairids"], passages["passageids"])
    return passage_objects


@app.get("/check_for_alignments/{philo_db}/")
def check_for_alignments(philo_db: str, philo_id: str):
    counts = aligner.check(philo_db, philo_id)
    return counts


@app.get("/search_texts")
def search_texts(request: Request):
    author = ""
    title = ""
    start_date = ""
    end_date = ""
    collections = ""
    periods = ""
    opbind = ""
    limit = 100
    if "author" in request.query_params:
        author = request.query_params["author"]
    if "title" in request.query_params:
        title = request.query_params["title"]
    if "collections" in request.query_params:
        collections = request.query_params["collections"]
    if "periods" in request.query_params:
        periods = request.query_params["periods"]
    if "date" in request.query_params:
        date = request.query_params["date"]
        dates = date.split("<=>")
        start_date = dates[0]
        try:
            end_date = dates[1]
        except IndexError:
            pass
    if "limit" in request.query_params:
        limit = int(request.query_params["limit"])
    if "binding" in request.query_params:
        opbind = request.query_params["binding"]
    if "words" in request.query_params:
        searchwords = request.query_params["words"]
        results, doc_count = search.word_search(
            searchwords, author, title, start_date, end_date, collections, periods, opbind, limit
        )
    else:
        results, doc_count = search.metadata_search(author, title, start_date, end_date, collections, periods, limit)
    return {"results": results, "doc_count": doc_count}


@app.get("/get_word_vectors/{word}")
def get_word_vectors(word: str):
    word_evolution, word_movers, overall_movers = get_word_evolution(word)
    return {"evolution": word_evolution, "movers": word_movers, "overall_movers": overall_movers}


@app.get("/get_similar_docs/{philo_db}")
def get_similar_docs(philo_db: str, philo_id: str):
    similar_docs = similarity.retrieve_similar_docs(philo_db, philo_id)
    return similar_docs


@app.post("/submit_passage")
def submit_passage(passage: Dict[str, str]):
    similar_docs = similarity.submit_passage(passage["passage"])
    return similar_docs


@app.get("/get_associated_words/{word}")
def get_associated_words(word: str):
    associated_words = retrieve_associated_words(word)
    return associated_words
