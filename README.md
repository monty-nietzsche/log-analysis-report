# Log-Analysis Report  by Montasser Ghachem
Assignment for Udacity Nanodegree (Full Stack Developer)

# Structure of the report
The report (output of the code report.py) consists of three parts:
- PART 1 lists the most popular articles of all time.
- PART 2 lists the most popular authors of all time.
- PART 3 lists the days in which the number of requests that lead to an error is higher than 1%.

[See a preview of the report](#report-preview)

# Parameters of the program report.py
To enrich the code, I have included 3 parameters:
- `TOP`: The number of popular articles that the user would like to show PART 1 of the report. If `TOP=4`, the report show the 4 most popular articles of all time in PART 1. The default value is 3, as asked in the assignment.
- `THRESHOLD`: This is the error rate threshold. In PART 3, the report will show the days that have an error rate (errors/requests) higher than this threshold. For instance, if `THRESHOLD=2`, then the report will show all days that have an error rate higher than 2%. The default value is `THRESHOLD=1`, as asked in the assignment.
- `ETOP`: This parameter specify the maximum number of days shown in the report. In case the threshold is very low (take `0.01%` for example), PART 3 might contain a large number of days having an error rate higher than this threshold. `ETOP` limits the number of the days shown in PART 3 of the report. If `THRESHOLD=0.5` and `ETOP=3`, the report shows the top three days with error rates higher than 0.5%. The default value is `ETOP=3`.

# Structure of the code
The code consists of four parts:
- Importing of psycopg2: `import psycopg2` 
- Declaration and initialization of the parameters: `DBNAME, TOP, THRESHOLD, ETOP`
- 3 functions extracting data from the database: [1] `Popular_articles()` [2] `Popular_authors()` [3] `Error_days()`
- 1 function printing the report: `Print_report()`

# Data functions
- `Popular_articles (TOP)`

    This function takes as argument the parameter `TOP (=3)` to return the list of the most popular articles and their number of views.     The length of the list has TOP as ceiling. The function calls DB-API, executes the following `SQL`query, and returns the result.

    ```sql
    select a.title, b.views from
     (select title, slug from articles) a 
     left join 
      (select path, count(*) as views from log where status LIKE '2%' and path!='/' group by path order by views desc) b
    on concat('/article/',a.slug)=b.path
  limit 3;"
    ``` 
    The number of views is obtained from the table log and is equal to all successful requests i.e. where `status=2xx`. Joining the     table `articles`and the table `log` is done through transforming `slug` in table `articles` into a path.

- `Popular_authors()`

  The function takes no argument and returns the list of the most popular authors and their number of views. The function calls DB-API,   executes the following `SQL`query, and returns the result.
  
  ```sql
  select c.name, sum(b.views) as total_views
  from 
    (select name, id from authors) c
    left join 
      (select author, title, slug from articles) a
      left join 
      (select path, count(*) as views from log where status LIKE '2%' and path!='/' group by path order by views desc) b
      on concat('/article/',a.slug)=b.path
    on a.author=c.id group by c.name 
  order by total_views desc; 
  ``` 
  The number of views for each other is obtained by summing the views of all articles he has written. Joining the tables `articles`and    `log` is done through transforming `slug` in table `articles` into a path. Joining the tables `authors` and `articles` is done through  the `articles.author` referencing `authors.id`. 

- `Error_days(THRESHOLD, ETOP)`

  The function takes two arguments `THRESHOLD` and `ETOP` and returns the list of all days in which the ratio of successful requests to total requests (error rate) is higher that `THRESHOLD`. The list returned cannot have a length higher than `ETOP`. The function calls DB-API, executes the following `SQL`query, and returns the result. Here `THRESHOLD=1`and `ETOP=3`.
  
  ```sql
  select a.day, a.requests, b.errors, b.errors*1./a.requests as rate
  from 
    (select date(time) as day, count(*) as requests from log group by day) a
    left join 
    (select date(time) as day, count(*) as errors from log where status NOT LIKE (%s) group by day) b
    on a.day=b.day 
  where b.errors*1./a.requests>0.01 
  order by rate desc 
  limit 3"
  ``` 
  The number of requests per day is obtained from the table `log` by grouping entries per day. The number of errors per day is the number of requests where `status!=2xx`. For each single day, dividing `errors` by `requests` gives the daily error rate `rate`. The days are then sorted by decreasing error rates. Finally, the first `ETOP` days with `rate>THRESHOLD` are selected and returned by the function.

# Report preview
```text
--------------------------------------- ----------------------------------------
------------------- Log Analysis Report By Montasser Ghachem -------------------
--------------------------------------- ----------------------------------------


The 3 most popular articles of all time:
 + Candidate is jerk, alleges rival - 338647 views
 + Bears love berries, alleges bear - 253801 views
 + Bad things gone, say good people - 170098 views


The most popular article authors of all time:
 + Ursula La Multa - 507594 views
 + Rudolf von Treppenwitz - 423457 views
 + Anonymous Contributor - 170098 views
 + Markoff Chaney - 84557 views


Days in which more than 1 % of requests lead to errors (Top 3):
 + Jul 17, 2016 - 2.3%  errors
    |- 1265 out of 55907 requests lead to errors.


-------------------- End of Report - Thanks for reviewing! ---------------------
```
