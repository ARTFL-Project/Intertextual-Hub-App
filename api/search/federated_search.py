#!/usr/bin/env python3

import codecs
import sys
import re
import cgi
from wsgiref.handlers import CGIHandler
from cgi import FieldStorage
from decimal import Decimal
import unidecode
import unicodedata
from mako.template import Template
from mako.lookup import TemplateLookup
import sqlite3


TABLE_NAME = "intertextual_hub_federated"


def de_accent(searchwords):
    sw2return = unicodedata.normalize("NFD", searchwords)
    sw2return = sw2return.encode("ascii", "ignore")
    sw2return = sw2return.decode("utf-8")
    return sw2return


def build_where_likes(start_date, end_date, collectionlimit, periodlimit):
    where_stmt_parts = []
    if collectionlimit:
        where_stmt_parts.append('philodbname LIKE "{0}"'.format(collectionlimit))
    if start_date:
        if end_date:
            where_stmt_parts.append('date BETWEEN "{0}" and "{1}"'.format(start_date, end_date))
        else:
            where_stmt_parts.append('date LIKE "{0}%"'.format(start_date))
    if periodlimit:
        where_stmt_parts.append('period LIKE "{0}"'.format(periodlimit))
    return where_stmt_parts


def build_match(searchwords, author, title):
    ## much formatting required to get column filtering syntax to work ##
    match_stmt_parts = []
    if searchwords:
        match_stmt_parts.append("(content:{0})".format(searchwords))
    if author:
        author = re.sub("[-,'\.:;]", " ", author)
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
        title = re.sub("[-,'\.:;]", " ", title)
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


def word_search(**query_params):
    print(execute_query(query_params["words"], "", "", "", "", "", "yes", "", "100", "", False))


def metadata_search(request):
    pass


########################################
## EXECUTE_QUERY: run psql query here ##
########################################


def execute_query(
    searchwords,
    author,
    title,
    start_date,
    end_date,
    opbind,
    showsnippets,
    collectionlimit,
    reslimit,
    periodlimit,
    bib_search,
):
    print(searchwords, file=sys.stderr)
    print(opbind, file=sys.stderr)

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

    print(searchwords, file=sys.stderr)
    print(collectionlimit, file=sys.stderr)
    print(author, file=sys.stderr)
    print(title, file=sys.stderr)

    query_terms = []
    snippets = "snippet({0}, 10, '<b>', '</b>', '...', 64)".format(TABLE_NAME)
    where_stmt_list = []
    fullcount_query = 0

    CONN = sqlite3.connect("../intertextual_hub_federated")
    CONN.text_factory = str
    cursor = CONN.cursor()

    if bib_search == 0:
        # print("Word search.", file=sys.stderr)
        select_vals = "filename, author, title, date, philoid, divhead, divdate, philodbname, bm25({0}), {1}".format(
            TABLE_NAME, snippets
        )
        searchwords = de_accent(searchwords)
        query_stmt = ""
        order_by = " order by bm25({0}) limit {1}".format(TABLE_NAME, reslimit)
        if opbind:
            searchwords = searchwords.replace(" ", " OR ")
        match_stmt_list = build_match(searchwords, author, title)
        match_stmt = " AND ".join(match_stmt_list)
        where_like_list = build_where_likes(start_date, end_date, collectionlimit, periodlimit)
        where_likes = " AND ".join(where_like_list)
        select_stmt = "SELECT {0} FROM {1} WHERE {1} MATCH ".format(select_vals, TABLE_NAME)
        if where_likes:
            query_stmt = select_stmt + "'" + match_stmt + "' AND " + where_likes + order_by
        else:
            query_stmt = select_stmt + "'" + match_stmt + "' " + order_by
        fullcount_query = 'SELECT COUNT(*) from {0} where {0} MATCH "{1}"'.format(TABLE_NAME, searchwords)

        print(query_stmt, file=sys.stderr)
        cursor.execute(query_stmt,)
        rows = cursor.fetchall()
        results_list = []
        count = 0
        for row in rows:
            count += 1
            filename = row[0]
            author = row[1]
            title = row[2]
            date = row[3]
            philoid = row[4]
            divhead = row[5]
            divdate = row[6]
            philodbname = row[7]
            score = row[8]
            headline = row[9]
            results_json = {
                "filename": filename,
                "author": author,
                "title": title,
                "date": date,
                "philoid": philoid,
                "divhead": divhead,
                "divdate": divdate,
                "philodbname": philodbname,
                "headline": headline,
                "score": score,
            }
            results_list.append(results_json)
        cursor.execute(fullcount_query,)
        doc_count = cursor.fetchone()

    ## handle bibliographic search ##

    else:
        print("Bib search.", file=sys.stderr)
        select_vals = "filename, author, title, date, philoid, divhead, divdate, philodbname"
        match_stmt_list = build_match(searchwords, author, title)
        match_stmt = " AND ".join(match_stmt_list)
        where_like_list = build_where_likes(start_date, end_date, collectionlimit, periodlimit)
        where_likes = " AND ".join(where_like_list)
        if match_stmt:
            select_stmt = "SELECT {0} FROM {1} WHERE {1} MATCH ".format(select_vals, TABLE_NAME)
            query_stmt = select_stmt + "'" + match_stmt + "'"
            if where_likes:
                query_stmt += " AND " + where_likes
        else:
            select_stmt = "SELECT {0} FROM {1} WHERE ".format(select_vals, TABLE_NAME)
            query_stmt = select_stmt + where_likes

        print(query_stmt, file=sys.stderr)
        cursor.execute(query_stmt,)
        rows = cursor.fetchall()
        results_list = []
        count = 0
        for row in rows:
            count += 1
            filename = row[0]
            author = row[1]
            title = row[2]
            date = row[3]
            philoid = row[4]
            divhead = row[5]
            divdate = row[6]
            philodbname = row[7]
            headline = ""
            score = 0
            results_json = {
                "filename": filename,
                "author": author,
                "title": title,
                "date": date,
                "philoid": philoid,
                "divhead": divhead,
                "divdate": divdate,
                "philodbname": philodbname,
                "headline": headline,
                "score": score,
            }
            results_list.append(results_json)

        doc_count = 0
    # print(fullcount_query, file=sys.stderr)

    # cursor.execute(fullcount_query,)
    # doc_count = 0
    # doc_count = cursor.fetchone()

    # print(doc_count, file=sys.stderr)

    return (results_list, count, doc_count)


#######################################
## RUN_QUERY: handle operations here ##
#######################################


def run_query(environ, start_response):

    form = cgi.FieldStorage()
    searchwords = form.getvalue("words")
    author = form.getvalue("author")
    title = form.getvalue("title")
    start_date = form.getvalue("start_date")
    end_date = form.getvalue("end_date")
    showsnippets = form.getvalue("showsnippets")
    opbind = form.getvalue("binding")
    collectionlimit = form.getvalue("collection")
    reslimit = form.getvalue("reslimit")
    periodlimit = form.getvalue("period")

    status = "200 OK"
    headers = [("Content-type", "text/html ;charset=UTF-8"), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    # header_template = templates.get_template("sqlite_header.html")
    # yield (header_template.render())
    # sw_display_template = templates.get_template("sw_webdisplay.mako")
    # bib_display_template = templates.get_template("bib_webdisplay.mako")

    results = ""
    count = 0
    doc_count = 0
    bail_out = 0
    for param in form:
        if re.search("[<>\(\){}=$]", form.getvalue(param)):
            bail_out = 1

    if searchwords:
        bib_search = 0
        if bail_out == 1:
            searchwords = "<ILLEGAL>"
            # yield (
            #     sw_display_template.render(
            #         results=results,
            #         searchwords=searchwords,
            #         count=count,
            #         opbind=opbind,
            #         collectionlimit=collectionlimit,
            #         periodlimit=periodlimit,
            #         doc_count=doc_count,
            #     )
            # )
        else:
            results, count, doc_count = execute_query(
                searchwords,
                author,
                title,
                start_date,
                end_date,
                opbind,
                showsnippets,
                collectionlimit,
                reslimit,
                periodlimit,
                bib_search,
            )
            # yield (
            #     sw_display_template.render(
            #         results=results,
            #         searchwords=searchwords,
            #         count=count,
            #         opbind=opbind,
            #         collectionlimit=collectionlimit,
            #         periodlimit=periodlimit,
            #         doc_count=doc_count,
            #         qauthor=author,
            #         qtitle=title,
            #         start_date=start_date,
            #         end_date=end_date,
            #     )
            # )
    else:
        bib_search = 1
        if bail_out == 1:
            searchwords = "<ILLEGAL>"
            yield (
                sw_display_template.render(
                    results=results,
                    searchwords=searchwords,
                    count=count,
                    opbind=opbind,
                    collectionlimit=collectionlimit,
                    periodlimit=periodlimit,
                    doc_count=doc_count,
                )
            )
        else:
            results, count, doc_count = execute_query(
                searchwords,
                author,
                title,
                start_date,
                end_date,
                opbind,
                showsnippets,
                collectionlimit,
                reslimit,
                periodlimit,
                bib_search,
            )
            yield (
                bib_display_template.render(
                    results=results,
                    searchwords=searchwords,
                    count=count,
                    opbind=opbind,
                    collectionlimit=collectionlimit,
                    periodlimit=periodlimit,
                    doc_count=doc_count,
                    qauthor=author,
                    qtitle=title,
                    start_date=start_date,
                    end_date=end_date,
                )
            )

    footer_template = templates.get_template("sqlite_footer.html")
    yield (footer_template.render())


##############
## __MAIN__ ##
##############

if __name__ == "__main__":
    CGIHandler().run(run_query)
