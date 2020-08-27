from typing import Dict, List, Union
import psycopg2
from psycopg2.extras import DictCursor


def get_word_evolution(word) -> Dict[int, List[Dict[str, Union[str, float]]]]:
    decades: Dict[str, List[Dict[str, Union[str, float]]]] = {}
    with psycopg2.connect(user="i_hub_user", password="martini", database="intertextual_hub",) as conn:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT decades FROM word_vectors_by_decade WHERE word=%s", (word,))
        decades = cursor.fetchone()["decades"]
    colored_decades: Dict[str, List[Dict[str, Union[str, float]]]] = {}
    for decade, words in decades.items():
        word_list = [(w["word"], w["weight"] * 10) for w in words]
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
            {"word": w[0], "size": w[1] / 10, "color": color_codes[w[1]]} for w in adjusted_word_list
        ]
        weighted_word_list.sort(key=lambda x: x["word"])
        colored_decades[decade] = weighted_word_list
    return colored_decades

