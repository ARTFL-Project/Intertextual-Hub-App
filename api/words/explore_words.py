import os
import sys
from typing import Dict, List, Tuple, Union

import numpy as np
import psycopg2
import requests
from Levenshtein import jaro_winkler
from psycopg2.extras import DictCursor
from unidecode import unidecode
from gensim.models import word2vec

sys.path.append("..")
from config import DB_CONFIG


DB_USER = DB_CONFIG["database_user"]
DB_NAME = DB_CONFIG["database_name"]
DB_PWD = DB_CONFIG["database_password"]
TOPOLOGIC = DB_CONFIG["topologic"]

MODELS = {
    "1700": word2vec.Word2Vec.load(DB_CONFIG["word2vec"]["1700"]),
    "1725": word2vec.Word2Vec.load(DB_CONFIG["word2vec"]["1725"]),
    "1750": word2vec.Word2Vec.load(DB_CONFIG["word2vec"]["1750"]),
    "1775": word2vec.Word2Vec.load(DB_CONFIG["word2vec"]["1775"]),
}


def get_word_evolution(
    words: str,
) -> Tuple[Dict[int, List[Dict[str, Union[str, float]]]], Dict[str, Dict[str, str]], Dict[str, str]]:
    periods: Dict[str, List[Dict[str, Union[str, float]]]] = {}
    vectors = {year: [] for year in MODELS.keys()}
    tokens = words.split()
    for year in vectors:
        vectors = []
        for word in tokens:
            word = unidecode(word)
            try:
                vectors.append(MODELS[year].wv.get_vector(word))
            except KeyError:
                pass
        if vectors:
            vector = np.mean(np.array(vectors), axis=0)
            matches = MODELS[year].wv.similar_by_vector(vector, topn=50 + len(tokens))
            periods[year] = [{"word": word, "weight": score} for word, score in matches if word not in tokens]

    word_map: Dict[str, int] = {}
    index_map: Dict[int, str] = {}
    index = 0
    for words in periods.values():
        for word in words:
            if word["word"] not in word_map:
                word_map[word["word"]] = index
                index_map[index] = word["word"]
                index += 1
    period_arrays: List[Dict[str, Union[str, np.array]]] = []
    for period, words in periods.items():
        local_array = np.array([0.0 for _ in word_map])
        for word in words:
            local_array[word_map[word["word"]]] = word["weight"]
        period_arrays.append({"period": period, "array": local_array})
    word_moves_recap: List[Dict[str, str]] = []
    for pos in range(len(periods)):
        current_array = period_arrays[pos]["array"]
        try:
            next_array = period_arrays[pos + 1]["array"]
        except IndexError:
            break
        diff = current_array - next_array
        max_move_up = index_map[np.argmin(diff)]
        max_move_down = index_map[np.argmax(diff)]
        word_moves_recap.append(
            {
                "max_up": max_move_up,
                "max_down": max_move_down,
                "period": f"{period_arrays[pos]['period']}-{period_arrays[pos+1]['period']}",
            }
        )
    first_last_diff = period_arrays[0]["array"] - period_arrays[-1]["array"]
    overall_movers: Dict[str, str] = {
        "max_up": index_map[np.argmin(first_last_diff)],
        "max_down": index_map[np.argmax(first_last_diff)],
    }

    colored_periods: Dict[str, List[Dict[str, Union[str, float]]]] = {}
    for period, words in periods.items():
        word_list = [(w["word"], w["weight"] * 10) for w in words[:50]]
        highest_value = word_list[0][1]
        if len(word_list) > 1:
            lowest_value = word_list[-1][1]
        else:
            lowest_value = 0
        coeff = (highest_value - lowest_value) / 10
        if coeff == 0.0:
            coeff = 1.0

        def adjust_weight(weight):
            adjusted_weight = round((weight - lowest_value) / coeff, 0)
            try:
                adjusted_weight = int(adjusted_weight)
            except ValueError:
                adjusted_weight = 0
            return adjusted_weight

        adjusted_word_list = [(w[0], adjust_weight(w[1])) for w in word_list]
        color_codes = {
            10: "rgb(143, 57, 49)",
            9: "rgba(143, 57, 49, .95)",
            8: "rgba(143, 57, 49, .9)",
            7: "rgba(143, 57, 49, .85)",
            6: "rgba(143, 57, 49, .8)",
            5: "rgba(143, 57, 49, .75)",
            4: "rgba(143, 57, 49, .7)",
            3: "rgba(143, 57, 49, .65)",
            2: "rgba(143, 57, 49, .6)",
            1: "rgba(143, 57, 49, .55)",
            0: "rgba(143, 57, 49, .5)",
        }

        weighted_word_list: List[Dict[str, Union[str, float]]] = [
            {"word": w[0], "size": w[1] / 10 - 0.1, "color": color_codes[w[1]]} for w in adjusted_word_list
        ]
        weighted_word_list.sort(key=lambda x: x["word"])
        colored_periods[period] = weighted_word_list

    return colored_periods, word_moves_recap, overall_movers


def retrieve_associated_words(word: str) -> Dict[str, str]:
    with psycopg2.connect(
        user=DB_CONFIG["database_user"], password=DB_CONFIG["database_password"], database=DB_CONFIG["database_name"],
    ) as conn:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT words FROM global_word_vectors WHERE word=%s", (word,))
        words: Dict[str, str] = cursor.fetchone()["words"]
    return words


def find_similar_words(word_to_match: str):
    """Edit distance function."""
    topologic_response = requests.get(
        os.path.join(TOPOLOGIC["api"], "get_all_field_values", TOPOLOGIC["dbname"]), params={"field": "word"}
    )
    words = topologic_response.json()["field_values"]
    similar_words: List[Tuple[str, float]] = []
    for word in words:
        similarity = jaro_winkler(word_to_match, word, 0.15)
        if similarity >= 0.85:
            similar_words.append((word, similarity))
    similar_words.sort(key=lambda x: x[1], reverse=True)
    return [word for word, _ in similar_words]
