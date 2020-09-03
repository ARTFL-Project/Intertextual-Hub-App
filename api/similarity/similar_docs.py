#!/usr/bin/env python3

import json
from typing import Dict, Union
from philologic.runtime.DB import DB
from philologic.runtime.get_text import get_text
from text_preprocessing import PreProcessor

from annoy import AnnoyIndex
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

with open("./db_config.json") as app_config:
    APP_CONFIG = json.load(app_config)

with open("../philo_to_annoy.json") as input_file:
    PHILO_ID_TO_ANNOY: Dict[str, Dict[str, str]] = json.load(input_file)

with open("../annoy_to_philo.json") as input_file:
    ANNOY_TO_PHILO_ID: Dict[str, Dict[str, str]] = json.load(input_file)

PREPROC = PreProcessor(
    modernize=True,
    language="french",
    ascii=False,
    min_word_length=3,
    lemmatizer="spacy",
    stopwords="/var/www/html/intertextual_hub/config/stopwords.txt",
)

INDEX = AnnoyIndex(1000, "angular")
INDEX.load("/shared/NEH_intertextual_hub/doc2vec-annoy/SEPT02clovis.annoy")

DOC2VEC_MODEL = Doc2Vec.load("/shared/NEH_intertextual_hub/doc2vec-annoy/SEPT01mvo03.model")


def process_annoy_results(newsims):
    simscores = list(newsims[1])
    matchdocs = list(newsims[0])
    results = []
    db_cache = {philo_db: DB(f'{config["path"]}/data') for philo_db, config in APP_CONFIG["philo_dbs"].items()}
    for doc, score in zip(matchdocs, simscores):
        doc_id = ANNOY_TO_PHILO_ID[str(doc)]
        hit = db_cache[doc_id["philo_db"]][doc_id["philo_id"]]
        results.append(
            {
                "philo_db": doc_id["philo_db"],
                "metadata": {
                    "author": hit.author,
                    "title": hit.title,
                    "date": hit.year,
                    "head": hit.head,
                    "philo_id": doc_id["philo_id"],
                },
                "score": score,
            }
        )
    return results


def retrieve_similar_docs(philo_db: str, philo_id: str, num: int = 10):
    philo_id = philo_id.strip()
    try:
        annoy_id = int(PHILO_ID_TO_ANNOY[philo_db][philo_id])
    except KeyError:
        db = DB(f"/var/www/html/intertextual_hub/philologic/{philo_db}/data")
        hit = db[philo_id]
        text = get_text(
            hit, hit.start_byte, hit.end_byte - hit.start_byte, f"/var/www/html/intertextual_hub/philologic/{philo_db}",
        )
        return submit_passage(text.decode("utf8"), num=10)
    newsims = INDEX.get_nns_by_item(annoy_id, num + 1, include_distances=True)
    results = process_annoy_results(newsims)
    return results[1:]


def submit_passage(passage: str, num: int = 20):
    processed_passage = " ".join(PREPROC.process_string(passage, keep_all=False)).split()
    search_vector = TaggedDocument(processed_passage, 0)
    inferred_vector = DOC2VEC_MODEL.infer_vector(search_vector[0])
    new_sims = INDEX.get_nns_by_vector(inferred_vector, num, include_distances=True)
    results = process_annoy_results(new_sims)
    return results
