#!/usr/bin/env python3

import re

import psycopg2
import psycopg2.extras
from typing import List, Dict, Union, Tuple
from dataclasses import dataclass
import rapidjson as json
from datetime import datetime

with open("./db_config.json") as db_config_file:
    db_config = json.load(db_config_file)
DB_USER = db_config["database_user"]
DB_NAME = db_config["database_name"]
DB_PWD = db_config["database_password"]
ALIGNMENTS_TABLE = db_config["alignments_table"]
PASSAGES_TABLE = db_config["passages_table"]

GROUP_BY_DOC = db_config["group_by_doc"]
# with open("../web-app/src/appConfig.json") as db_config_file:
#     app_config = json.load(db_config_file)
# GROUP_BY_LEVELS = app_config["groupByLevels"]
# OBJECT_LEVELS = {db: value["object_type"] for db, value in app_config["philoDBs"].items()}


FIELD_TYPES = {
    "source_philo_db": {"type": "TEXT"},
    "target_philo_db": {"type": "TEXT"},
    "source_author": {"type": "TEXT"},
    "target_author": {"type": "TEXT"},
    "source_title": {"type": "TEXT"},
    "target_title": {"type": "TEXT"},
    "source_head": {"type": "TEXT"},
    "target_head": {"type": "TEXT"},
    "source_date": {"type": "DATE"},
    "target_date": {"type": "DATE"},
    "source_philo_id": {"type": "TEXT"},
    "target_philo_id": {"type": "TEXT"},
    # "source_philo_type": "TEXT",
    # "target_philo_type": "TEXT",
    "pairid": {"type": "TEXT"},
    "passages": {"type": "JSONB"},
}

BOOLEAN_ARGS = re.compile(r"""(NOT \w+)|(OR \w+)|(\w+)|("")""")
DATE_RANGE = re.compile(r"<=>")

FILTERED_QUERY_WORDS = {
    "a",
    "à",
    "au",
    "aux",
    "avec",
    "ce",
    "ces",
    "cette",
    "comme",
    "d",
    "dans",
    "de",
    "du",
    "en",
    "il",
    "ils",
    "la",
    "le",
    "les",
    "mais",
    "ne",
    "ou",
    "par",
    "pas",
    "plus",
    "pour",
    "que",
    "qui",
    "sur",
    "un",
    "une",
}


@dataclass
class Passage:
    start_byte: int
    end_byte: int
    metadata: List[Dict[str, str]]


def query_builder(query_args: dict):
    """Takes query arguments and returns an SQL WHERE clause"""
    sql_fields = []
    sql_values = []
    for field, value in query_args.items():
        value = value.strip()
        field_type = FIELD_TYPES[field]["type"]
        query = ""
        if field_type == "TEXT":
            for not_query, or_query, regular_query, empty_query in BOOLEAN_ARGS.findall(value):
                if not_query != "":
                    value = not_query
                elif or_query != "":
                    value = or_query
                elif empty_query != "":
                    value = empty_query
                else:
                    value = regular_query
                if value.startswith('"'):
                    if value == '""':
                        query = f"{field} = %s"
                        sql_values.append("")
                    else:
                        query = f"{field}=%s"
                        sql_values.append(value[1:-1])
                elif value.startswith("NOT "):
                    split_value = " ".join(value.split()[1:]).strip()
                    query = f"{field} !~* %s"
                    sql_values.append(fr"\m{split_value}\M")
                # elif value.startswith("OR "):  ## TODO: add support to OR queries by changing the join logic at the end of the function
                #     split_value = " ".join(value.split()[1:]).strip()
                #     query = "{} !~* %s".format(field)
                #     sql_values.append('\m{}\M'.format(split_value))
                else:
                    query = f"{field} ~* %s"
                    if value in FILTERED_QUERY_WORDS:
                        continue
                    sql_values.append(fr"\m{value}\M")
                sql_fields.append(query)
        elif field_type == "INTEGER" or field_type == "FLOAT":
            value = value.replace('"', "")
            if "-" in value:
                values = [v for v in re.split(r"(-)", value) if v]
                if values[0] == "-":
                    query = f"{field} <= %s"
                    sql_values.append(values[1])
                elif values[-1] == "-":
                    query = f"{field} >= %s"
                    sql_values.append(values[0])
                else:
                    query = f"{field} BETWEEN %s AND %s"
                    sql_values.extend([values[0], values[2]])
            else:
                query = f"{field} = %s"
                sql_values.append(value)
            sql_fields.append(query)
        elif field_type == "DATE":
            if "<=>" in value:
                low, high = DATE_RANGE.split(value)
                if low.isdigit():
                    low = f"{low}-01-01"
                if high.isdigit():
                    high = f"{high}-12-31"
                sql_fields.append(f"{field} BETWEEN %s AND %s")
                sql_values.extend((low, high))
            else:
                if value.isdigit():
                    value = f"{value}-01-01"
                sql_fields.append(f"{field} = %s")
                sql_values.append(value)
        else:
            continue
    # if other_args.banality != "":
    #     sql_fields.append("banality=%s")
    #     sql_values.append(other_args.banality)
    return " AND ".join(sql_fields), sql_values


def search_alignments(**query_params):
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql_fields, sql_values = query_builder(query_params)
        query = f"SELECT {', '.join(FIELD_TYPES.keys())} FROM {ALIGNMENTS_TABLE} WHERE {sql_fields}"
        cursor.execute(query, sql_values)
        results = []
        for row in cursor:
            metadata = {field: row[field] for field in FIELD_TYPES if field != "passages"}
            metadata["passage_number"] = len(row["passages"])
            results.append(metadata)
    return results


def search_alignments2(**query_params):
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql_fields, sql_values = query_builder(query_params)
        query = f"SELECT {', '.join(FIELD_TYPES.keys())} FROM {ALIGNMENTS_TABLE} WHERE {sql_fields}"
        cursor.execute(query, sql_values)
        results = []
        current_source_doc: str = ""
        current_target_doc: str = ""
        title_pair: str = ""
        current_title_pair: str = ""
        metadata_list = []
        passages: int = 0
        doc_metadata = {}
        for row in cursor:
            source_philo_db: str = row["source_philo_db"]
            target_philo_db: str = row["target_philo_db"]
            if source_philo_db in GROUP_BY_DOC:
                current_source_doc = row["source_title"]
            else:
                current_source_doc = f"""{row["source_author"]}{row["source_head"]}{row["source_title"]}"""
            if target_philo_db in GROUP_BY_DOC:
                current_target_doc = row["target_title"]
            else:
                current_target_doc = f"""{row["target_author"]}{row["target_head"]}{row["target_title"]}"""
            current_title_pair = f"{current_source_doc}-{current_target_doc}"
            if not title_pair:
                title_pair = current_title_pair
            if current_title_pair != title_pair and title_pair:
                results.append(
                    {
                        "metadata_list": metadata_list,
                        "doc_metadata": doc_metadata,
                        "passage_number": passages,
                        "source_philo_db": row["source_philo_db"],
                        "target_philo_db": row["target_philo_db"],
                    }
                )
                title_pair = current_title_pair
                passages = 0
                metadata_list = []
            passages += len(row["passages"])
            doc_metadata = {
                "source_title": row["source_title"],
                "source_author": row["source_author"],
                "source_date": row["source_date"],
                "target_title": row["target_title"],
                "target_author": row["target_author"],
                "target_date": row["target_date"],
            }
            metadata_list.append(
                {
                    "source_head": row["source_head"],
                    "source_div_date": row["source_date"],
                    "source_philo_id": row["source_philo_id"],
                    "target_head": row["target_head"],
                    "target_div_date": row["target_date"],
                    "target_philo_id": row["target_philo_id"],
                    "pairid": row["pairid"],
                }
            )
        results.append({"metadata_list": metadata_list, "doc_metadata": doc_metadata})
    return results


def get_passages(pairid: str):
    """Get passages by pairid"""
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT passages FROM {PASSAGES_TABLE} WHERE pairid=%s", (pairid,))
        passages = cursor.fetchone()[0]
        # TODO: have a way to sort the passages by source_start_byte
        return [
            {
                "passageid": passage["passageid"],
                "source_context_before": passage["source_context_before"],
                "source_passage": passage["source_passage"],
                "source_context_after": passage["source_context_after"],
                "target_context_before": passage["target_context_before"],
                "target_passage": passage["target_passage"],
                "target_context_after": passage["target_context_after"],
            }
            for passage in passages
        ]


def get_passage_by_philo_id(
    object_id: List[str], direction: str, philo_db: str
) -> Union[
    Tuple[
        List[Dict[str, int]],
        List[List[Dict[str, Union[str, datetime]]]],
        Dict[str, Union[str, datetime]],
        List[Union[Dict[str, Union[str, datetime]], str]],
    ],
    Tuple[None, None, None, None],
]:
    """Get all passage bytes offsets by philo_id"""
    zeros_to_add = " ".join(["0" for _ in range(7 - len(object_id))])
    philo_id: str = f"{' '.join(object_id)} {zeros_to_add}"

    doc_metadata: Dict[str, Union[str, datetime]] = {}
    if direction == "source":
        opposite_direction = "target"
    else:
        opposite_direction = "source"
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        passages: List[Tuple[int, int, Dict[str, Union[str, datetime]]]] = []
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(
            f"SELECT * FROM {ALIGNMENTS_TABLE} WHERE {direction}_philo_id=%s AND {direction}_philo_db=%s",
            (philo_id, philo_db),
        )
        for row in cursor:
            local_metadata = {
                field: row[field] for field in FIELD_TYPES if not field.startswith(direction) and field != "passages"
            }
            local_offsets: List[Tuple[int, int, Dict[str, Union[str, datetime]]]] = [
                (
                    int(passage[f"{direction}_start_byte"]),
                    int(passage[f"{direction}_end_byte"]),
                    {**local_metadata, "passageid": passage["passageid"]},
                )
                for passage in row["passages"]
            ]
            passages.extend(local_offsets)
            if not doc_metadata:
                doc_metadata = {
                    field: row[field]
                    for field in FIELD_TYPES
                    if not field.startswith(opposite_direction) and field not in ("pairid", "passages")
                }

        passages.sort(key=lambda x: (x[0], x[1]))

    if not passages:
        return None, None, None, None

    current_passage: Dict[str, int] = {"start_byte": passages[0][0], "end_byte": passages[0][1]}
    passage_groups: List[Dict[str, int]] = []
    metadata_list: List[List[Dict[str, Union[str, datetime]]]] = [[passages[0][2]]]
    for start_byte, end_byte, metadata in passages:
        if start_byte < current_passage["end_byte"] and end_byte > current_passage["end_byte"]:
            current_passage["end_byte"] = end_byte
            metadata_list[len(passage_groups)].append(metadata)
        elif start_byte >= current_passage["end_byte"]:
            passage_groups.append(current_passage)
            current_passage = {"start_byte": start_byte, "end_byte": end_byte}
            metadata_list.append([metadata])
    passage_groups.append(current_passage)
    for pos, _ in enumerate(metadata_list):
        metadata_list[pos].sort(key=lambda x: x[f"{opposite_direction}_date"])

    author_titles: Dict[str, List[Dict[str, Union[str, datetime]]]] = {}
    for group in metadata_list:
        for doc in group:
            author_title = doc[f"{opposite_direction}_author"] + "_" + doc[f"{opposite_direction}_title"]
            if author_title not in author_titles:
                author_titles[author_title] = [doc]
            else:
                author_titles[author_title].append(doc)
    docs_cited: List[Union[Dict[str, Union[str, datetime]], str]] = [
        {
            "doc_metadata": {
                f"{opposite_direction}_author": metadata[0][f"{opposite_direction}_author"],
                f"{opposite_direction}_title": metadata[0][f"{opposite_direction}_title"],
            },
            "metadata": metadata,
            "direction": opposite_direction,
        }
        for metadata in author_titles.values()
    ]
    return passage_groups, metadata_list, doc_metadata, docs_cited


def get_passage_byte_offsets(pairid: str, direction: str):
    """Get passage byte offsets by pairid"""
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT {', '.join(FIELD_TYPES.keys())} FROM {ALIGNMENTS_TABLE} WHERE pairid=%s", (pairid,))
        results = cursor.fetchone()
        passages = results[-1]
        offsets = [
            {"start_byte": int(passage[f"{direction}_start_byte"]), "end_byte": int(passage[f"{direction}_end_byte"]),}
            for passage in passages
        ]
        metadata = {field: results[index] for index, field in enumerate(FIELD_TYPES)}
    return {"passages": offsets, "metadata": metadata}


def get_passage(pairid: str, start_byte: int, direction: str):
    """Get single passage by pairid and start byte"""
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT passages FROM {ALIGNMENTS_TABLE} WHERE pairid=%s", (pairid,))
        row = cursor.fetchone()[0]
        passageid = None
        for passage in row:
            if int(passage[f"{direction}_start_byte"]) == start_byte:
                passageid = passage["passageid"]
        cursor.execute(f"SELECT passages FROM {PASSAGES_TABLE} WHERE pairid=%s", (pairid,))
        passages = cursor.fetchone()[0]
        passage = {}
        for passage_object in passages:
            if passage_object["passageid"] == passageid:
                passage = passage_object
                break
        cursor.execute(f"SELECT * FROM {ALIGNMENTS_TABLE} WHERE pairid=%s", (pairid,))
        results = cursor.fetchone()
        passage["metadata"] = {field: results[index] for index, field in enumerate(FIELD_TYPES)}
    return passage


def get_passages_by_pairids_and_passageids(pairids: List[str], passageids: List[str]) -> List[Dict[str, str]]:
    with psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    ) as conn:
        cursor = conn.cursor()
        passage_objects: List[Dict[str, str]] = []
        for pairid, passageid in zip(pairids, passageids):
            cursor.execute(f"SELECT passages FROM {PASSAGES_TABLE} WHERE pairid=%s", (pairid,))
            passages: List[Dict[str, str]] = cursor.fetchone()[0]
            for passage_object in passages:
                if passage_object["passageid"] == passageid:
                    passage_objects.append(passage_object)
                    break
    return passage_objects

