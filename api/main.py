from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from collections import defaultdict
import json
import requests
from urllib.parse import quote

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/navigate")
def navigate(request: Request):
    response = requests.get(
        f"""https://anomander.uchicago.edu/text-pair-api/retrieve_all_passage_pairs/?db_table=frantext18thc_vs_frc&source_philo_id={quote(request.query_params["source_philo_id"])}&target_philo_id={quote(request.query_params["target_philo_id"])}"""
    )
    passages = []
    if request.query_params["direction"] == "source":
        link = f"""https://anomander.uchicago.edu/intertextual_hub/frantext18thc/reports/navigation.py?philo_id={quote(request.query_params["source_philo_id"])}"""
    else:
        link = f"""https://anomander.uchicago.edu/intertextual_hub/frc/reports/navigation.py?philo_id={quote(request.query_params["target_philo_id"])}"""
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
    query_string = "&".join(
        [f"{key}={value}" for key, value in request.query_params.items()]
    )
    response = requests.get(
        f"https://anomander.uchicago.edu/text-pair-api/retrieve_all_passage_pairs/?db_table=frantext18thc_vs_frc&{query_string}"
    )
    grouped_alignments = defaultdict(list)
    for alignment in response.json():
        combined_id = (
            f"""{alignment["source_philo_id"]}-{alignment ["target_philo_id"] }"""
        )
        grouped_alignments[combined_id].append(alignment)
    return {"results": list(grouped_alignments.values())}
