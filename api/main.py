from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from collections import defaultdict
import json
import requests
from urllib.parse import quote

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

HUB_URL = "https://anomander.uchicago.edu/intertextual_hub/"
TEXT_PAIR_API = "https://anomander.uchicago.edu/text-pair-api/"
SOURCE_DB = "hub18thcfrench"
TARGET_DB = "frc"
ALIGNMENT_DB = "frantext18thc_vs_frc"


@app.get("/navigate")
def navigate(request: Request):
    response = requests.get(
        f"{TEXT_PAIR_API}/retrieve_all_passage_pairs/",
        params={
            "db_table": ALIGNMENT_DB,
            "source_philo_id": request.query_params["source_philo_id"],
            "target_philo_id": request.query_params["target_philo_id"],
        },
    )
    print("RESPONSE", response.url)
    print(
        "STRING",
        f"""{TEXT_PAIR_API}/retrieve_all_passage_pairs/?db_table={ALIGNMENT_DB}&source_philo_id={quote(request.query_params["source_philo_id"])}&target_philo_id={quote(request.query_params["target_philo_id"])}""",
    )
    passages = []
    if request.query_params["direction"] == "source":
        link = f"{HUB_URL}/{SOURCE_DB}/reports/navigation.py?philo_id={quote(request.query_params['source_philo_id'])}"
        for alignment in response.json():
            passages.append(
                {
                    "start_byte": alignment["source_start_byte"],
                    "end_byte": alignment["source_end_byte"],
                    "rowid": alignment["rowid"],
                }
            )
    else:
        link = f"{HUB_URL}/{TARGET_DB}/reports/navigation.py?philo_id={quote(request.query_params['target_philo_id'])}"
        for alignment in response.json():
            passages.append(
                {
                    "start_byte": alignment["target_start_byte"],
                    "end_byte": alignment["target_end_byte"],
                    "rowid": alignment["rowid"],
                }
            )
    philologic_response = requests.post(link, json={"passages": passages})
    return philologic_response.json()


@app.get("/search")
def search(request: Request):
    query_params = {"db_table": ALIGNMENT_DB, **request.query_params}
    response = requests.get(f"{TEXT_PAIR_API}/retrieve_all_passage_pairs/", params=query_params)
    grouped_alignments = defaultdict(list)
    for alignment in response.json():
        combined_id = f"""{alignment["source_philo_id"]}-{alignment ["target_philo_id"] }"""
        grouped_alignments[combined_id].append(alignment)
    return {"results": list(grouped_alignments.values())}
