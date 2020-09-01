from typing import Dict, List, Union, Tuple
import psycopg2
from psycopg2.extras import DictCursor
import numpy as np


def get_word_evolution(
    word,
) -> Tuple[Dict[int, List[Dict[str, Union[str, float]]]], Dict[str, Dict[str, str]], Dict[str, str]]:
    periods: Dict[str, List[Dict[str, Union[str, float]]]] = {}
    with psycopg2.connect(user="i_hub_user", password="martini", database="intertextual_hub",) as conn:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT periods FROM word_vectors_by_quarter WHERE word=%s", (word,))
        periods = cursor.fetchone()["periods"]

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
    print(len(period_arrays))
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
            {"word": w[0], "size": w[1] / 10 - 0.1, "color": color_codes[w[1]]} for w in adjusted_word_list
        ]
        weighted_word_list.sort(key=lambda x: x["word"])
        colored_periods[period] = weighted_word_list

    return colored_periods, word_moves_recap, overall_movers

