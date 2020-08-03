import requests
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import aligner
import search
from psycopg2.pool import ThreadedConnectionPool
import json
from typing import Optional
import databases

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

HUB_URL = "https://anomander.uchicago.edu/intertextual_hub/"


@app.get("/navigate/{philo_db}/{pairid}/{direction}")
def navigate(philo_db: str, pairid: str, direction: str, philo_id: str):
    passage_data = aligner.get_passage_byte_offsets(pairid, direction)
    text_object_id = philo_id.split("/")
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
        "metadata": passage_data["metadata"],
    }


@app.get("/search_alignments")
def search_alignments(request: Request):
    results = aligner.search_alignments(**request.query_params)
    return results[:50]


@app.get("/retrieve_passages/{pairid}")
def retrieve_passages(pairid: str):
    passages = aligner.get_passages(pairid)
    return passages


@app.get("/retrieve_passage/{pairid}")
def retrieve_passage(pairid: str, start_byte: int, direction: str):
    passage = aligner.get_passage(pairid, start_byte, direction)
    return passage


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
