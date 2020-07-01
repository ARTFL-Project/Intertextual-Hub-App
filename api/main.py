import json
from collections import defaultdict
from typing import List, Dict

import requests
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from alignments import search_alignments, get_passages, get_passage_byte_offsets, get_passage

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

HUB_URL = "https://anomander.uchicago.edu/intertextual_hub/"


@app.get("/navigate/{philo_db}/{pairid}/{direction}")
async def navigate(philo_db: str, pairid: str, direction: str, philo_id: str):
    passage_data = get_passage_byte_offsets(pairid, direction)
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


@app.get("/search")
async def search(request: Request):
    results = search_alignments(**request.query_params)
    return results[:50]


@app.get("/retrieve_passages/{pairid}")
async def retrieve_passages(pairid: str):
    passages = get_passages(pairid)
    return passages


@app.get("/retrieve_passage/{pairid}")
async def retrieve_passage(pairid: str, start_byte: int, direction: str):
    passage = get_passage(pairid, start_byte, direction)
    return passage
