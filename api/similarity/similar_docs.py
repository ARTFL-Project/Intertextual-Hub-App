#!/usr/bin/env python3

import os
import pickle
from typing import Dict, List, Union

import rapidjson
from annoy import AnnoyIndex
from philologic.runtime.DB import DB
from philologic.runtime.get_text import get_text
from sklearn.feature_extraction.text import TfidfVectorizer
from text_preprocessing import PreProcessor

from api.config import DB_CONFIG, APP_CONFIG, PHILO_PATHS


with open(os.path.join(DB_CONFIG["doc_id_mapping"], "philo_to_annoy.json")) as input_file:
    PHILO_ID_TO_ANNOY: Dict[str, Dict[str, str]] = rapidjson.load(input_file)
with open(os.path.join(DB_CONFIG["doc_id_mapping"], "annoy_to_philo.json")) as input_file:
    ANNOY_TO_PHILO_ID: Dict[str, Dict[str, str]] = rapidjson.load(input_file)

PREPROC = PreProcessor(
    modernize=True,
    language="french",
    ascii=True,
    min_word_length=3,
    lemmatizer="spacy",
    stopwords="/var/www/html/intertextual_hub/config/stopwords.txt",
)

with open(DB_CONFIG["tfidf_model"], "rb") as vectorizer:
    TF_IDF_VECTORIZER: TfidfVectorizer = pickle.load(vectorizer)

INDEX = AnnoyIndex(len(TF_IDF_VECTORIZER.vocabulary_), "angular")
INDEX.load(DB_CONFIG["annoy_index"])


def process_annoy_results(newsims) -> List[Dict[str, Union[str, Dict[str, str]]]]:
    simscores = list(newsims[1])
    matchdocs = list(newsims[0])
    results: List[Dict[str, Union[str, Dict[str, str]]]] = []
    db_cache = {philo_db: DB(f'{config["path"]}/data') for philo_db, config in APP_CONFIG["philoDBs"].items()}
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


def retrieve_similar_docs(philo_db: str, philo_id: str, num: int = 20):
    philo_id = philo_id.strip()
    try:
        annoy_id = int(PHILO_ID_TO_ANNOY[philo_db][philo_id])
    except KeyError:
        db = DB(f"{PHILO_PATHS[philo_db]}/data")
        hit = db[philo_id]
        text = get_text(hit, hit.start_byte, hit.end_byte - hit.start_byte, PHILO_PATHS[philo_db],)
        return submit_passage(text.decode("utf8"), num=num)
    newsims = INDEX.get_nns_by_item(annoy_id, num + 1, include_distances=True)
    results = process_annoy_results(newsims)
    return results[1:]


def submit_passage(passage: str, num: int = 20):
    processed_passage = " ".join(PREPROC.process_string(passage, keep_all=False))
    passage_vector = TF_IDF_VECTORIZER.transform([processed_passage]).toarray()[0]
    new_sims = INDEX.get_nns_by_vector(passage_vector, num, include_distances=True)
    results = process_annoy_results(new_sims)
    return results
