#!/usr/bin/env python3
import psycopg2


# DBNAME is the database name to connect to
DBNAME = "news"

# TOP is the number of popular articles one would like to show
TOP = 3

# THRESHOLD is the threshold of error rates per day, it is a number that
# represents the percentage threshold of errors per day. If THRESHOLD = 2, we
# are looking for days where the error rate (percentage of requests leading to
# errors) is equal or larger than 2%. ETOP represents the maximum
# number of days that is shown having an error rate higher than THRESHOLD.
THRESHOLD = 1
ETOP = 3


def popular_articles(TOP):
    """
    queries the log database to extract the list of the popular articles
    where popularity is  measured by the number of views each article has
    over the whole time period covered in the database. The list returned
    has at most TOP rows.

    args:
        TOP - (integer) the maximum number of rows in the return list

    returns:
        A list of tuples (articles, views) sorted in a descending order of
        views i.e. articles with larger number of views show first.
    """

    args = ['2%', TOP]
    query = """
    SELECT a.title, b.views
    FROM
    (SELECT title, slug FROM articles) a
    LEFT JOIN
    (SELECT path, COUNT(*) AS views FROM log WHERE status LIKE (%s)
    AND path != '/' GROUP BY path ORDER BY views DESC) b
    ON concat('/article/',a.slug) = b.path
    LIMIT (%s);"""
    return execute_query(query, args)


def popular_authors():
    """
    queries the log database to extract the most popular authors where
    popularity is measured by the total number of views that their articles
    have.

    returns:
        A list of tuples (authors, total_views) sorted in a descending order
        i.e. authors with larger number of views show first.
    """

    args = ['2%']
    query = """
    SELECT c.name, SUM(b.views) AS total_views
    FROM
    authors c
    LEFT JOIN
        articles a
        LEFT JOIN
        (SELECT path, COUNT(*) AS views FROM log WHERE status LIKE (%s)
        and path != '/' GROUP BY path ORDER BY views DESC) b
        ON concat('/article/',a.slug) = b.path
    ON a.author = c.id
    GROUP BY c.name
    ORDER BY total_views DESC;"""
    return execute_query(query, args)


def error_days(THRESHOLD, ETOP):
    """
    queris the log database to find the days during which the error rate
    (ratio of erronous requests over total requests) exceeds a threshold.
    The list returned has at most ETOP rows.

    args:
        THRESHOLD - (integer) the error rate threshold above which a day
                    is selected.
        ETOP - (integer) the maximum number of rows included in the
                returned list

    returns
        A list of tuples (days, requests, errors, error rate) having an
        error_rate higher than THRESHOLD. The list sorted in a descending
        order i.e. days with larger error_rate show first. The list has at
        most ETOP rows.
    """
    args = ['2%', THRESHOLD*0.01, ETOP]
    query = """
    SELECT a.day, a.requests, b.errors, b.errors*1./a.requests as error_rate
    FROM
    (SELECT date(time) AS day, COUNT(*) AS requests FROM log
    GROUP BY day) a
    LEFT JOIN
    (SELECT date(time) AS day, COUNT(*) AS errors
    FROM log WHERE status NOT LIKE (%s) GROUP BY day) b
    ON a.day = b.day
    WHERE b.errors*1./a.requests>(%s)
    ORDER BY error_rate DESC
    LIMIT (%s);
    """
    return execute_query(query, args)


def execute_query(query, data=[]):
    """
    execute_query takes an SQL query as a parameter,
    executes the query and returns the results as a list of tuples.

    args:
      query - (string) an SQL query statement to be executed.
      data - (list) a list of parameters to pass into the query statement.

    returns:
      A list of tuples containing the results of the query.
    """
    try:
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        c.execute(query, data)
        stats = c.fetchall()
        db.close()
        return stats

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def Print_report(TOP, THRESHOLD, ETOP):

    line = " + %s - %s %s"
    print("\033c")  # clear screen

    # Header of the report
    print('{:-^80}'.format(' '))
    print('{:-^80}'.format(' Log Analysis Report By Montasser Ghachem '))
    print('{:-^80}'.format(' '))
    print("\n")

    # Answer to Question 1
    print("The %i most popular articles of all time:" % TOP)
    stats = popular_articles(TOP)
    for article, views in stats:
        print (line % (article, views, "views"))
    print("\n")

    # Answer to Question 2
    print("The most popular article authors of all time:")
    authors = popular_authors()
    for article, views in authors:
        print (line % (article, views, "views"))
    print("\n")

    # Answer to Question 3
    print("Days with %s %% or more erronous requests:" % THRESHOLD)
    days = error_days(THRESHOLD, ETOP)
    if not days:
        print(" + None")    # If the list of days is empty, write 'None'
    if days:
        for day, requests, errs, rate in days:
            print (line % (day.strftime("%b %d, %Y"),
                           '{:.1%}'.format(rate),
                           " errs"))
            print ("  (%s out of %s requests are erronous)" % (errs, requests))
        print("\n")

    # Footer of the report
    print('{:-^80}'.format(' End of Report - Thanks for reviewing! '))

if __name__ == '__main__':
    Print_report(TOP,THRESHOLD,ETOP)
