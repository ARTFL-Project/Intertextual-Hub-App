from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

import json
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
def read_root():
    response = requests.get(
        "https://anomander.uchicago.edu/text-pair-api/retrieve_all_passage_pairs/?target_title=pot%20noir&db_table=frantext18thc_vs_frc&source_author=helvétius"
    )
    passages = []
    link = "https://anomander.uchicago.edu/intertextual_hub/frc/reports/navigation.py?philo_id=1153%201"
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
    print(repr([(key, value) for key, value in request.query_params.items()]))
    response = requests.get(
        "https://anomander.uchicago.edu/text-pair-api/retrieve_all_passage_pairs/?target_title=pot%20noir&db_table=frantext18thc_vs_frc&source_author=helvétius"
    )
    passages = []
    # link = "https://anomander.uchicago.edu/intertextual_hub/frc/reports/navigation.py?philo_id=1153%201"
    # for alignment in response.json():
    #     passages.append(
    #         {
    #             "start_byte": alignment["target_start_byte"],
    #             "end_byte": alignment["target_end_byte"],
    #             "rowid": alignment["rowid"],
    #         }
    #     )
    # philologic_response = requests.post(link, json={"passages": passages})
    # return philologic_response.json()
