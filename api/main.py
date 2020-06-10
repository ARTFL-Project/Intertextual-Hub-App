from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from collections import defaultdict
import json
import requests

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
    passages = get_passages(request)
    if request.query_params["direction"] == "source":
        philologic_response = requests.post(
            f"{HUB_URL}/{SOURCE_DB}/reports/navigation.py",
            params={"philo_id": request.query_params["source_philo_id"]},
            json={"passages": passages},
        )
    else:
        philologic_response = requests.post(
            f"{HUB_URL}/{TARGET_DB}/reports/navigation.py",
            params={"philo_id": request.query_params["target_philo_id"]},
            json={"passages": passages},
        )
    return philologic_response.json()


@app.get("/search")
def search(request: Request):
    grouped_alignments = get_all_passages(request)
    return grouped_alignments


def get_passages(request):
    """Get passages from TextPAIR"""
    response = requests.get(
        f"{TEXT_PAIR_API}/retrieve_all_passage_pairs/",
        params={
            "db_table": ALIGNMENT_DB,
            "source_philo_id": request.query_params["source_philo_id"],
            "target_philo_id": request.query_params["target_philo_id"],
        },
    )
    direction = request.query_params["direction"]

    passages = []
    for alignment in response.json():
        passages.append(
            {
                "start_byte": alignment[f"{direction}_start_byte"],
                "end_byte": alignment[f"{direction}_end_byte"],
                "rowid": alignment["rowid"],
            }
        )
    return passages


def get_all_passages(request):
    """Retrieve all passages based on query and group by doc pairs"""
    query_params = {"db_table": ALIGNMENT_DB, **request.query_params}
    response = requests.get(f"{TEXT_PAIR_API}/retrieve_all_passage_pairs/", params=query_params)
    grouped_alignments = {}
    for alignment in response.json():
        combined_id = f"""{alignment["source_philo_doc_id"]}-{alignment ["target_philo_doc_id"] }"""
        print(combined_id)
        if combined_id not in grouped_alignments:
            grouped_alignments[combined_id] = {"alignment_count": 1, **alignment}
        else:
            grouped_alignments[combined_id]["alignment_count"] += 1
    return grouped_alignments
