import requests
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import aligner
import search
from typing import List, Optional, Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

HUB_URL = "https://anomander.uchicago.edu/intertextual_hub/"

PHILO_TYPE = {1: "doc", 2: "div1", 3: "div2"}


@app.get("/navigate/{philo_db}")
def navigate(
    philo_db: str, philo_id: str, direction: str, pairid: Optional[str] = None, intertextual: Optional[bool] = None,
):
    text_object_id: List[str] = philo_id.split()
    if pairid is not None:
        passage_data = aligner.get_passage_byte_offsets(pairid, direction)
        while text_object_id[-1] == "0":
            text_object_id.pop()
        philologic_response = requests.post(
            f"{HUB_URL}/philologic/{philo_db}/reports/navigation.py",
            params={"philo_id": " ".join(text_object_id)},
            json={"passages": passage_data["passages"]},
        )
        philo_text_object = philologic_response.json()
        return {
            "text": philo_text_object["text"],
            "intertextual_metadata": [[passage_data["metadata"]] for _ in passage_data["metadata"]["passages"]],
            "doc_metadata": {
                field: value for field, value in passage_data["metadata"].items() if field.startswith(direction)
            },
        }
    elif intertextual is True:
        passage_data, metadata_list, doc_metadata, docs_cited = aligner.get_passage_by_philo_id(
            text_object_id, direction, philo_db
        )
        if passage_data is None:
            philologic_response = requests.post(
                f"{HUB_URL}/philologic/{philo_db}/reports/navigation.py", params={"philo_id": " ".join(text_object_id)},
            )
            philo_text_object = philologic_response.json()
            return {
                "text": philo_text_object["text"],
                "doc_metadata": {
                    f"{direction}_philo_db": philo_db,
                    f"{direction}_philo_id": " ".join(text_object_id),
                    f"{direction}_date": philo_text_object["metadata_fields"]["year"],
                    **{f"{direction}_{field}": value for field, value in philo_text_object["metadata_fields"].items()},
                },
                "intertextual_metadata": [],
            }
        philologic_response = requests.post(
            f"{HUB_URL}/philologic/{philo_db}/reports/navigation.py",
            params={"philo_id": " ".join(text_object_id)},
            json={"passages": passage_data},
        )
        philo_text_object = philologic_response.json()
        return {
            "text": philo_text_object["text"],
            "intertextual_metadata": metadata_list,
            "doc_metadata": doc_metadata,
            "docs_cited": docs_cited,
        }


@app.get("/search_alignments")
def search_alignments(request: Request):
    results = aligner.search_alignments(**request.query_params)
    return results[:50]


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


@app.get("/search_texts")
def search_texts(request: Request):
    author = ""
    title = ""
    start_date = ""
    end_date = ""
    collections = ""
    periods = ""
    opbind = ""
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
    if "binding" in request.query_params:
        opbind = request.query_params["binding"]
    if "words" in request.query_params:
        searchwords = request.query_params["words"]
        results, doc_count = search.word_search(
            searchwords, author, title, start_date, end_date, collections, periods, opbind
        )
    else:
        results, doc_count = search.metadata_search(author, title, start_date, end_date, collections, periods)
    return {"results": results, "doc_count": doc_count}
