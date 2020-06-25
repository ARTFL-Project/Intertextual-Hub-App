#!/usr/bin/env python3

import re

import psycopg2
import psycopg2.extras
import rapidjson as json

with open("./db_config.json") as db_config_file:
    db_config = json.load(db_config_file)
    db = psycopg2.connect(
        user=db_config["database_user"], password=db_config["database_password"], database=db_config["database_name"],
    )
CURSOR = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
TABLE = db_config["alignments_table"]

FIELD_TYPES = {
    "source_author": "TEXT",
    "target_author": "TEXT",
    "source_title": "TEXT",
    "target_title": "TEXT",
    "source_head": "TEXT",
    "target_head": "TEXT",
    "source_date": "DATE",
    "target_date": "DATE",
    "source_philo_db": "TEXT",
    "target_philo_db": "TEXT",
    "source_philo_id": "TEXT",
    "target_philo_id": "TEXT",
    # "source_philo_type": "TEXT",
    # "target_philo_type": "TEXT",
    "pairid": "TEXT",
    "passages": "JSONB",
}

BOOLEAN_ARGS = re.compile(r"""(NOT \w+)|(OR \w+)|(\w+)|("")""")


def query_builder(query_args):
    """Takes query arguments and returns an SQL WHERE clause"""
    sql_fields = []
    sql_values = []
    for field, value in query_args.items():
        value = value.strip()
        field_type = FIELD_TYPES[field]
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
                        query = "{} = %s".format(field)
                        sql_values.append("")
                    else:
                        query = "{}=%s".format(field)
                        sql_values.append(value[1:-1])
                elif value.startswith("NOT "):
                    split_value = " ".join(value.split()[1:]).strip()
                    query = "{} !~* %s".format(field)
                    sql_values.append("\m{}\M".format(split_value))
                # elif value.startswith("OR "):  ## TODO: add support to OR queries by changing the join logic at the end of the function
                #     split_value = " ".join(value.split()[1:]).strip()
                #     query = "{} !~* %s".format(field)
                #     sql_values.append('\m{}\M'.format(split_value))
                else:
                    query = "{} ~* %s".format(field)
                    sql_values.append("\m{}\M".format(value))
                sql_fields.append(query)
        elif field_type == "INTEGER" or field_type == "FLOAT":
            value = value.replace('"', "")
            if "-" in value:
                values = [v for v in re.split(r"(-)", value) if v]
                if values[0] == "-":
                    query = "{} <= %s".format(field)
                    sql_values.append(values[1])
                elif values[-1] == "-":
                    query = "{} >= %s".format(field)
                    sql_values.append(values[0])
                else:
                    query = "{} BETWEEN %s AND %s".format(field)
                    sql_values.extend([values[0], values[2]])
            else:
                query = "{} = %s".format(field)
                sql_values.append(value)
            sql_fields.append(query)
        else:
            continue
    # if other_args.banality != "":
    #     sql_fields.append("banality=%s")
    #     sql_values.append(other_args.banality)
    return " AND ".join(sql_fields), sql_values


def search_alignments(**query_params):
    print(query_params)
    sql_fields, sql_values = query_builder(query_params)
    query = f"SELECT * FROM {TABLE} WHERE {sql_fields}"
    CURSOR.execute(query, sql_values)
    results = []
    for row in CURSOR:
        metadata = {field: row[field] for field in FIELD_TYPES if field != "passages"}
        metadata["passage_number"] = len(row["passages"])
        results.append(metadata)
    return results


def get_passages(pairid):
    CURSOR.execute(f"SELECT passages FROM {TABLE} WHERE pairid=%s", (pairid,))
    passages_info = [passage for passage in CURSOR]
    return [
        {
            "source_context_before": "PLACEHOLDER CONTEXT BEFORE",
            "source_passage": "PLACEHOLDER passage",
            "source_passage_after": "PLACEHOLDER CONTEXT AFTER",
            "target_context_before": "PLACEHOLDER CONTEXT BEFORE",
            "target_passage": "PLACEHOLDER passage",
            "target_passage_after": "PLACEHOLDER CONTEXT AFTER",
        }
        for _ in enumerate(passages_info)
    ]


def get_passage_byte_offsets(pairid, direction):
    CURSOR.execute(f"SELECT passages FROM {TABLE} WHERE pairid=%s", (pairid,))
    passages = CURSOR.fetchone()[0]
    byte_offsets = []
    return [
        {"start_byte": int(passage[f"{direction}_start_byte"]), "end_byte": int(passage[f"{direction}_end_byte"])}
        for passage in passages
    ]
