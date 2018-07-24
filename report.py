import psycopg2


# DBNAME is the database name to connect to
DBNAME="news"

# TOP is the number of popular articles one would like to show
TOP=3

# THRESHOLD is the threshold of error rates per day, it is a number that
# represents the percentage threshold of errors per day. If THRESHOLD=2 then we
# are looking for days where the error rate (the percentage of requests leading to
# errors) is equal or larger than 2%. ETOP in the integer that represents the maxium
# number of days that is shown having an error rate higher than THRESHOLD. 
THRESHOLD=1
ETOP=3



def popular_articles(a_number):
    db=psycopg2.connect(database=DBNAME)
    c=db.cursor()
    sql="select a.title, b.views from (select title, slug from articles) a left join (select path, count(*) as views from log where status LIKE (%s) and path!='/' group by path order by views desc) b on concat('/article/',a.slug)=b.path limit (%s);"
    args= ['2%', a_number]
    c.execute(sql,args)
    stats= c.fetchall()
    db.close()
    return stats

def popular_authors():
    db=psycopg2.connect(database=DBNAME)
    c=db.cursor()
    c.execute("select c.name, sum(b.views) as total_views from (select name, id from authors) c left join (select author, title, slug from articles) a left join (select path, count(*) as views from log where status LIKE (%s) and path!='/' group by path order by views desc) b on concat('/article/',a.slug)=b.path on a.author=c.id group by c.name order by total_views desc;",('2%',))
    stats= c.fetchall()
    db.close()
    return stats

def error_days(threshold,etop):
    db=psycopg2.connect(database=DBNAME)
    c=db.cursor()
    threshold=threshold*0.01 #transform the threshold into a decimal
    args=['2%',threshold,etop]
    c.execute ("select a.day, a.requests, b.errors, b.errors*1./a.requests as rate from (select date(time) as day, count(*) as requests from log group by day) a left join (select date(time) as day, count(*) as errors from log where status NOT LIKE (%s) group by day) b on a.day=b.day where b.errors*1./a.requests>(%s) order by rate desc limit (%s)",args)
    stats= c.fetchall()
    db.close()
    return stats

def Print_report (TOP,THRESHOLD,ETOP):

    line =" + %s - %s %s"

    print("\033c")  # clear screen

    # Header of the report
    print('{:-^80}'.format(' ')  )
    print('{:-^80}'.format(' Log Analysis Report By Montasser Ghachem ')  )
    print('{:-^80}'.format(' ')  )

    print("\n")

    # Answer to Question 1

    print("The %i most popular articles of all time:" % TOP)
    stats=popular_articles(TOP)
    for article, views in stats:
        print (line %(article, views, "views"))

    print("\n")

    # Answer to Question 2

    print("The most popular article authors of all time:")
    authors=popular_authors()
    for article, views in authors:
        print (line %(article, views,"views"))

    print("\n")

    # Answer to Question 3

    print("Days in which more than %s %% of requests lead to errors (Top %s):" % (THRESHOLD, ETOP))
    days=error_days(THRESHOLD,ETOP)
    if not days:
        print(" + None")    # If the list of days is empty, write 'None'
    if days:
        for day, requests, errors, rate in days:
            print (line %(day.strftime("%b %d, %Y"), '{:.1%}'.format(rate)," errors"))
            print ("    |- %s out of %s requests lead to errors." % (errors, requests))

    print("\n")

    # Footer of the report
    print('{:-^80}'.format(' End of Report - Thanks for reviewing! ')  )

Print_report(TOP,THRESHOLD,ETOP)