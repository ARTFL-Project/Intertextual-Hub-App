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
ALIGNMENTS_TABLE = db_config["alignments_table"]
PASSAGES_TABLE = db_config["passages_table"]


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
DATE_RANGE = re.compile(r"<=>")


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
    print(sql_fields, sql_values)
    return " AND ".join(sql_fields), sql_values


def search_alignments(**query_params):
    print(query_params)
    sql_fields, sql_values = query_builder(query_params)
    query = f"SELECT * FROM {ALIGNMENTS_TABLE} WHERE {sql_fields}"
    CURSOR.execute(query, sql_values)
    results = []
    for row in CURSOR:
        metadata = {field: row[field] for field in FIELD_TYPES if field != "passages"}
        metadata["passage_number"] = len(row["passages"])
        results.append(metadata)
    return results


def get_passages(pairid):
    CURSOR.execute(f"SELECT passages FROM {PASSAGES_TABLE} WHERE pairid=%s", (pairid,))
    passages = CURSOR.fetchone()[0]
    return [
        {
            "passageid": passage["passageid"],
            "source_context_before": passage["source_context_before"],
            "source_passage": passage["source_passage"],
            "source_passage_after": passage["source_context_after"],
            "target_context_before": passage["target_context_before"],
            "target_passage": passage["target_passage"],
            "target_passage_after": passage["target_context_after"],
        }
        for passage in passages
    ]


def get_passage_byte_offsets(pairid, direction):
    CURSOR.execute(f"SELECT passages FROM {ALIGNMENTS_TABLE} WHERE pairid=%s", (pairid,))
    passages = CURSOR.fetchone()[0]
    byte_offsets = []
    return [
        {"start_byte": int(passage[f"{direction}_start_byte"]), "end_byte": int(passage[f"{direction}_end_byte"])}
        for passage in passages
    ]


def get_passage(pairid, passage_number, direction):
    CURSOR.execute(f"SELECT passages FROM {PASSAGES_TABLE} WHERE pairid=%s", (pairid,))
    passages = CURSOR.fetchone()[0]
    passageid = f"{pairid}:{passage_number}"
    passage = {}
    for passage_object in passages:
        if passage_object["passageid"] == passageid:
            passage = passage_object
            break
    CURSOR.execute(f"SELECT * FROM {ALIGNMENTS_TABLE} WHERE pairid=%s", (pairid,))
    results = CURSOR.fetchone()
    passage["metadata"] = {field: results[field] for field in FIELD_TYPES}
    return passage

