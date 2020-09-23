#!/usr/bin/env python3

import sys
import re
import json
import unicodedata
import sqlite3

with open("../web-app/src/appConfig.json") as db_config_file:
    app_config = json.load(db_config_file)
GROUP_BY_LEVELS = app_config["groupByLevels"]
OBJECT_LEVELS = {db: value["object_type"] for db, value in app_config["philoDBs"].items()}

with open("./db_config.json") as db_config_file:
    db_config = json.load(db_config_file)
DB_FILE = db_config["federated_search_index"]

TABLE_NAME = "intertextual_hub_federated"


def de_accent(searchwords):
    sw2return = unicodedata.normalize("NFD", searchwords)
    sw2return = sw2return.encode("ascii", "ignore")
    sw2return = sw2return.decode("utf-8")
    return sw2return


def build_where_likes(start_date, end_date, collectionlimit, periodlimit):
    where_stmt_parts = []
    if collectionlimit:
        where_stmt_parts.append('philo_db = "{0}"'.format(collectionlimit))
    if start_date:
        if end_date:
            where_stmt_parts.append('date BETWEEN "{0}" and "{1}"'.format(start_date, end_date))
        else:
            where_stmt_parts.append('date LIKE "{0}%"'.format(start_date))
    if periodlimit:
        where_stmt_parts.append('period = "{0}"'.format(periodlimit))
    return where_stmt_parts


def build_match(searchwords, author, title):
    ## much formatting required to get column filtering syntax to work ##
    match_stmt_parts = []
    if searchwords:
        match_stmt_parts.append("(content:{0})".format(searchwords))
    if author:
        author = re.sub(r"[-,'.:;]", " ", author)
        if re.search(" OR ", author):
            OR_stmt_parts = []
            OR_authors = author.split(" OR ")
            for OR_author in OR_authors:
                if re.search(" ", OR_author):
                    OR_stmt_parts.append("author:NEAR({0})".format(OR_author))
                else:
                    OR_stmt_parts.append("author:{0}".format(OR_author))
            match_stmt_parts.append("({0})".format(" OR ".join(OR_stmt_parts)))
        elif re.search(" ", author):
            match_stmt_parts.append("(author:NEAR({0}))".format(author))
        else:
            match_stmt_parts.append("(author:{0})".format(author))
    if title:
        title = re.sub(r"[-,'.:;]", " ", title)
        if re.search(" OR ", title):
            OR_stmt_parts = []
            OR_titles = title.split(" OR ")
            for OR_title in OR_titles:
                if re.search(" ", OR_title):
                    OR_stmt_parts.append("title:NEAR({0})".format(OR_title))
                else:
                    OR_stmt_parts.append("title:{0}".format(OR_title))
            match_stmt_parts.append("({0})".format(" OR ".join(OR_stmt_parts)))
        elif re.search(" ", title):
            match_stmt_parts.append("(title:NEAR({0}))".format(title))
        else:
            match_stmt_parts.append("(title:{0})".format(title))
    return match_stmt_parts


def retrieve_section_names(cursor, filename, philo_db):
    cursor.execute(
        f"""SELECT distinct head, philo_id, div_date FROM {TABLE_NAME} WHERE {TABLE_NAME} MATCH '(filename:"{filename}") AND (philo_db:"{philo_db}")'"""
    )
    results = [
        {"head": row["head"], "philo_id": row["philo_id"], "div_date": row["div_date"], "philo_db": philo_db}
        for row in cursor
    ]
    return results


def word_search(searchwords, author, title, start_date, end_date, collections, periods, opbind, limit):

    got_metadata_OR = 0
    got_author_OR = 0
    got_title_OR = 0

    try:
        if re.search(" OR ", author):
            got_metadata_OR = 1
            got_author_OR = 1
    except:
        pass

    try:
        if re.search(" OR ", title):
            got_metadata_OR = 1
            got_title_OR = 1
    except:
        pass

    query_terms = []
    snippets = "snippet({0}, 13, '<b>', '</b>', '...', 64)".format(TABLE_NAME)
    where_stmt_list = []
    fullcount_query = 0

    with sqlite3.connect(DB_FILE) as conn:
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # print("Word search.", file=sys.stderr)
        select_vals = "filename, author, title, date, philo_id, head, div_date, philo_db, bm25({0}), {1}".format(
            TABLE_NAME, snippets
        )
        searchwords = de_accent(searchwords)
        query_stmt = ""
        order_by = " order by bm25({0}) limit {1}".format(TABLE_NAME, limit)
        if opbind:
            searchwords = searchwords.replace(" ", " OR ")
        match_stmt_list = build_match(searchwords, author, title)
        match_stmt = " AND ".join(match_stmt_list)
        where_like_list = build_where_likes(start_date, end_date, collections, periods)
        where_likes = " AND ".join(where_like_list)
        select_stmt = "SELECT {0} FROM {1} WHERE {1} MATCH ".format(select_vals, TABLE_NAME)
        if where_likes:
            query_stmt = select_stmt + "'" + match_stmt + "' AND " + where_likes + order_by
        else:
            query_stmt = select_stmt + "'" + match_stmt + "' " + order_by
        fullcount_query = 'SELECT COUNT(*) from {0} where {0} MATCH "{1}"'.format(TABLE_NAME, searchwords)

        cursor.execute(query_stmt,)
        results_list = []
        count = 0
        for row in cursor:
            count += 1
            score = row[8]
            headline = row[9]
            results_json = {
                "author": row["author"] or "",
                "title": row["title"],
                "date": row["date"],
                "philo_id": row["philo_id"],
                "head": row["head"],
                "div_date": row["div_date"] or "",
                "philo_db": row["philo_db"],
                "headline": headline,
                "score": score,
            }
            results_list.append(results_json)
        cursor.execute(fullcount_query,)
        doc_count = cursor.fetchone()
    return results_list, doc_count[0]


def metadata_search(author, title, start_date, end_date, collections, periods, limit):
    select_vals = "filename, author, title, date, philo_id, philo_db"
    match_stmt_list = build_match("", author, title)
    match_stmt = " AND ".join(match_stmt_list)
    where_like_list = build_where_likes(start_date, end_date, collections, periods)
    where_likes = " AND ".join(where_like_list)
    if match_stmt:
        select_stmt = "SELECT {0} FROM {1} WHERE {1} MATCH ".format(select_vals, TABLE_NAME)
        query_stmt = select_stmt + "'" + match_stmt + "'"
        if where_likes:
            query_stmt += " AND " + where_likes
    else:
        select_stmt = "SELECT {0} FROM {1} WHERE ".format(select_vals, TABLE_NAME)
        query_stmt = select_stmt + where_likes
    query_stmt += f" GROUP BY author, title ORDER BY date, filename LIMIT {limit}"

    with sqlite3.connect(DB_FILE) as conn:
        conn.text_factory = str
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        with sqlite3.connect(DB_FILE) as secondary_conn:
            secondary_conn.text_factory = str
            secondary_conn.row_factory = sqlite3.Row
            secondary_cursor = secondary_conn.cursor()
            cursor.execute(query_stmt,)
            results_list = []
            count = 0
            for row in cursor:
                count += 1
                philo_db = row["philo_db"]
                sections = []
                if OBJECT_LEVELS[philo_db] != GROUP_BY_LEVELS[philo_db]:
                    sections = retrieve_section_names(secondary_cursor, row["filename"], philo_db)
                results_list.append(
                    {
                        "author": row["author"] or "",
                        "title": row["title"],
                        "date": row["date"],
                        "philo_id": row["philo_id"],
                        "philo_db": philo_db,
                        "sections": sections,
                        "score": 0,
                    }
                )
    return results_list, count

