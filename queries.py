import ast
import datetime
import datetime
import mysql
import mysql.connector

DEFAULT_VALUE=0
CURRENT_DAY='2021-01-09%'
import configparser
my_config_parser = configparser.ConfigParser()
my_config_parser.read('config.ini')

mydb = mysql.connector.connect(
        host=my_config_parser.get('DEFAULT','sql_host'),
        user=my_config_parser.get('DEFAULT','sql_user'),
        password=my_config_parser.get('DEFAULT','sql_password'),
        database = my_config_parser.get('DEFAULT','sql_db')
    )

db_cursor = mydb.cursor(buffered=True)

def main():
    return 1

# return worldwide info:cases,deaths,todayCases,todayDeaths,precents
def worldWideData():
    statement = "SELECT JSON_OBJECT('cases',t1.cases,'precentCases',(t1.cases/ t3.p * 100),'todayCases',IFNULL(t2.todayCases,0),\
	            'deaths',t1.deaths,'precentDeaths',(t1.deaths / t3.p * 100),'todayDeaths',IFNULL(t2.todayDeaths,0))\
                from \
                (SELECT sum(Cases) as cases,sum(Deaths) as deaths FROM `team14`.`covid-19`) as t1,\
                (SELECT sum(Cases) as todayCases, sum(Deaths) as todayDeaths FROM `team14`.`covid-19` where Date=%s) \
                as t2,(SELECT sum(Population) as p FROM `team14`.`countries`) as t3;"
    result_set=error_handling(statement,(CURRENT_DAY,),"get")
    return result_set

#return country info by id :cases,todaycases,deaths,todayDeaths,lat,long,precents
def countryData(id):
    statement = "SELECT  JSON_OBJECT('cases',cases,'precentCases',(`cases`/ `p` * 100) , 'todayCases',IFNULL(`todayCases`,0), \
	            'deaths',deaths,'precentDeaths',(`deaths` / `p` * 100),'todayDeaths',IFNULL(`todayDeaths`,0),'lat',LAT,\
                'long',`LONG`) from   \
                 ((SELECT `ID_Country`,sum(Cases) as cases,sum(Deaths) as deaths  \
                 FROM `team14`.`covid-19` where ID_Country = %s) as tSum \
                 left join (SELECT `ID_Country`,Cases as todayCases, Deaths as todayDeaths  \
                 FROM `team14`.`covid-19` where Date=%s and ID_Country =%s) as tToday \
                 on tSum.ID_Country =tToday.ID_Country \
                 left join (SELECT `ID_Country`,Population as p ,`LAT`,`LONG` \
                 FROM `team14`.`countries` where ID_Country = %s) as tCountry on  tSum.`ID_Country`=tCountry.`ID_Country`);"

    result_set=error_handling(statement,(id,CURRENT_DAY,id,id),"get")
    return result_set


# return countries info about info :cases,deaths,lat,long,flag_url,country name,id
def countriesData():
    statement="SELECT JSON_OBJECT('value',`ID_Country`,'cases',`cases`,'deaths',`deaths`,'lat',`LAT`,'long',`LONG`,'flag',`flag_url` \
            ,'country',tCountry.Country_Name) \
            FROM ((SELECT `ID_Country`, SUM(`Cases`) as cases ,SUM(`Deaths`) as deaths \
             From `team14`.`covid-19` Group by ID_Country) tSum \
            left join (SELECT `ID_Country` as id,Country_Name,`LAT`,`LONG`,`FLAG_url`  from `team14`.`countries`) tCountry \
            on tSum.`ID_Country`= tCountry.`id`);"

    result_set=error_handling(statement,None,"get")
    return result_set


# return the countries sorted in des order by cases
def countriesSorted():
    statement = "SELECT JSON_OBJECT('country',Country_Name,'cases',Cases) From (SELECT * FROM " \
                "(SELECT ID_Country AS ID, SUM(Cases) As Cases \
                FROM `team14`.`covid-19`\
                group by ID_Country) as T\
                left join `team14`.`countries` as C on C.ID_Country = T.ID) as h order by Cases DESC;"

    result_set=error_handling(statement,None,"get")
    return result_set


# find the date num backwords
def findStartDay(num_back):
    sub_statement = "SELECT DATE_ADD(%s, INTERVAL - %s DAY) AS startDate"
    start_date=error_handling(sub_statement,(CURRENT_DAY, num_back),"get")
    if(start_date is not None):
        start_date = str(start_date[0][0]) + "%"
    return  start_date


# return historical info accorandliy to the user demend -chose case and num days back
def historyInfo(Num_Backword_days,case):
    start_date=findStartDay(Num_Backword_days)
    if(start_date is not None):
        dateFormat="%m/%d/%y"
        if(case=='Cases' or case=='cases'):
            statement="SELECT JSON_OBJECT('x',DATE_FORMAT(`Date`,%s),'y' ,Sum(Cases))FROM `team14`.`covid-19` WHERE " \
                      "`Date` between %s  and %s GROUP BY Date;"
        else:
            statement = "SELECT JSON_OBJECT('x',DATE_FORMAT(`Date`,%s),'y' ,Sum(Deaths))FROM `team14`.`covid-19` WHERE " \
                        "`Date` between %s and %s GROUP BY Date;"

        result_set = error_handling(statement,(dateFormat,start_date,CURRENT_DAY),"get")
    else:
        return None
    return result_set



# return the active polls which need to be shown
def activePolls():
    statement = "SELECT JSON_OBJECT('id', id_question, 'ques', question, 'yes', `count_yes`, 'no', `count_no`)\
                FROM ( SELECT * FROM `team14`.`polls_data` WHERE `mode`=1) AS T;"

    result_set = error_handling(statement,None,"get")
    return result_set


# update the poll count accord to the answer received
def updatePollCount(id,answer):
    if(answer=='yes'):
        statement = "UPDATE `team14`.`polls_data` SET `count_yes` = `count_yes` +1 WHERE id_question=%s;"
    else:
        statement = "UPDATE `team14`.`polls_data` SET `count_no` = `count_no` +1 WHERE id_question=%s;"

    noError=error_handling(statement,(id,),"update")
    if(noError):
        check = db_cursor.rowcount
    else:
        # will be none
        check=noError
    return check


# return o or 1 -check if the pass and user exists
def checkLogin(user,passw):
    statement="SELECT COUNT(1) \
                FROM `team14`.managers \
                WHERE User=%s and password=%s;"
    result=error_handling(statement,(user,passw),"get")
    if(result is not None):
        result=result[0][0]
    return result


# return all the polls in the db
def allPolls():
    statement ="SELECT JSON_OBJECT('id' ,id_question, 'title',question,'yes',`count_yes`,'no',`count_no`,'mode', if(mode=1, true, false) )\
                 FROM `team14`.`polls_data`;"
    result_set = error_handling(statement,None,"get")
    return result_set


# add new poll ,return the id he got
def addPoll(qeus):
    statement= 'INSERT INTO `team14`.`polls_data` (`question`,`count_yes`,`count_no`,`mode`) \
               VALUES (%s,%s,%s,%s);'
    noError=error_handling(statement,(qeus,DEFAULT_VALUE,DEFAULT_VALUE,DEFAULT_VALUE),"update")
    if(noError):
        # return the id of the poll we added
        result = db_cursor.lastrowid
    else:
        # will be none
        result=noError
    return result

# update poll to be hide or show,true-show
def updatePollMode(mode,id):
    # print(approved)
    statement = "UPDATE `team14`.`polls_data` SET mode=(%s) WHERE id_question=(%s);"
    noError=error_handling(statement,(mode,id),"update")
    if(noError):
        check=db_cursor.rowcount
    else:
        check=noError
    return check


# delete poll
def deletePoll(id):
    statement = "DELETE FROM `team14`.`polls_data` WHERE `polls_data`.id_question=(%s);"
    noError=error_handling(statement,(id,),"update")
    if(noError):
        check=db_cursor.rowcount
    else:
        check=noError
    return check

# return the material graph data - oil,gas,bitcoin,cases,deaths worldwide daily
def materialGraph(num_back):
    start_date=findStartDay(num_back)
    dateFormat = "%m/%d/%y"
    statement="SELECT JSON_OBJECT('date',DATE_FORMAT(`Date`,%s), 'bitcoin',Bitcoin,'gas',Gas,'oil',Oil, \
               'cases',Cases, 'deaths',Deaths) FROM \
                (SELECT Date as Date_c ,sum(Cases) as Cases,sum(Deaths) as Deaths \
              from `team14`.`covid-19` group by Date) as tCovid \
             left join (SELECT * FROM `team14`.`global_daily` )as tGlobal \
             on tGlobal.Date = tCovid.Date_c \
             WHERE `Date` between %s and %s;"

    result_set=error_handling(statement,(dateFormat, start_date, CURRENT_DAY),"get")
    return result_set


# return the material graph data - oil,gas,bitcoin,cases,deaths worldwide daily in prop
def materialGraphProp(num_back):
    start_date = findStartDay(num_back)
    dateFormat = "%m/%d/%y"
    statement="SELECT JSON_OBJECT('date',DATE_FORMAT(`Date`, %s), 'bitcoin',(Bitcoin/5000),'gas',Gas,'oil',(Oil /20), \
                'cases',(Cases/100000) ,'deaths',(Deaths/4000) ) \
              FROM (SELECT Date as Date_c ,sum(Cases) as Cases,sum(Deaths) as Deaths \
              from `team14`.`covid-19` group by Date) as tCovid \
             left join (SELECT * FROM `team14`.`global_daily` )as tGlobal \
             on tGlobal.Date = tCovid.Date_c \
             WHERE `Date` between %s and %s;"
    result_set = error_handling(statement, (dateFormat, start_date, CURRENT_DAY), "get")
    return result_set


# return the finance graph data given num days back and the id of a country -monthly
def financeGraph(num_back,id_country):
    dateFormat1 = "%Y-%m"
    dateFormat2 = "%Y-%m-01"
    start_date=findStartDay(num_back)
    if(start_date is not None):
        start_date=start_date[:-4]
        #  the info about unemployment and finance is base on month,every 01 in a month
        start_date=start_date+"-01%"
        statement="SELECT JSON_OBJECT('date',DATE_FORMAT(tFinance.`Date`, %s),'finance',tFinance.finance,'unemployment', tFinance.unemployment, \
                     'cases',tCovid.cases, 'deaths',tCovid.deaths) \
                    from (select DATE_FORMAT(`Date`,%s ) as month, ID_Country as ID, sum(cases) as cases ,sum(deaths) as deaths \
                    from `team14`.`covid-19` WHERE `covid-19`.ID_Country=%s group by `month`,ID) as tCovid \
                    left join (SELECT * FROM `team14`.`global_monthly` WHERE `global_monthly`.ID_country=%s) as tFinance \
                    on (tFinance.ID_Country = tCovid.ID and  tFinance.Date = tCovid.month) \
                    where (tFinance.ID_Country = tCovid.ID and  tFinance.Date = tCovid.month and tFinance.Date between %s and %s ); "

        result_set=error_handling(statement,(dateFormat1,dateFormat2,id_country,id_country,start_date, CURRENT_DAY),"get")
    else:
        return None
    return result_set


# return the finance graph data given num days back and the id of a country -monthly prop
def financeGraphProp(num_back,id_country):
    dateFormat1 = "%Y-%m"
    dateFormat2 = "%Y-%m-01"
    start_date=findStartDay(num_back)
    if(start_date is not None):
        start_date=start_date[:-4]
        #  the info about unemployment and finance is base on month,every 01 in a month
        start_date=start_date+"-01%"
        statement="SELECT JSON_OBJECT('date',DATE_FORMAT(tFinance.`Date`, %s),'finance',(tFinance.finance/20),'unemployment', \
                    tFinance.unemployment,'cases',(tCovid.cases/10000), 'deaths',(tCovid.deaths/2000)) \
                    from (select DATE_FORMAT(`Date`,%s ) as month, ID_Country as ID, sum(cases) as cases ,sum(deaths) as deaths \
                    from `team14`.`covid-19` WHERE `covid-19`.ID_Country=%s group by `month`,ID) as tCovid \
                    left join (SELECT * FROM `team14`.`global_monthly` WHERE `global_monthly`.ID_country=%s) as tFinance \
                    on (tFinance.ID_Country = tCovid.ID and  tFinance.Date = tCovid.month) \
                    where (tFinance.ID_Country = tCovid.ID and  tFinance.Date = tCovid.month and tFinance.Date between %s and %s ); "

        result_set=error_handling(statement,(dateFormat1,dateFormat2,id_country,id_country,start_date, CURRENT_DAY),"get")
    else:
        return None
    return result_set



# return the mainland sorted by cases from highest to lowest
def mainlandSorted():
    statement="SELECT JSON_OBJECT('cases',sumC,'region',Name_region) \
                FROM (select sum(cases) as sumC,Name_region \
                From((select ID_Country,sum(cases) as cases FROM `team14`.`covid-19` group by ID_Country)as tCovid \
               left join (select ID_Country,ID_Region FROM `team14`.`countries`)as tCountry \
               on tCovid.ID_Country=tCountry.ID_Country \
               left join \
             (select Name_region,ID_Region FROM `team14`.`mainlands` ) as tReiogns \
              on tCountry.ID_Region=tReiogns.ID_Region ) \
             group by Name_region order by sumC DESC) as t;"

    result_set=error_handling(statement,None,"get")
    return result_set

#  return the countries that can be chosen in the finance graph
def countriesFinance():
    statement="SELECT JSON_OBJECT('value',id ,'country',country) \
                FROM(SELECT distinct id,country \
                FROM ( SELECT ID_Country as id fROM `team14`.global_monthly) as h \
                 left join (select ID_Country,Country_Name as country FROM `team14`.`countries` ) as t \
                 on h.id=t.ID_Country) AS result ;"

    result_set=error_handling(statement,None,"get")
    return result_set


# return none if error occurred
def error_handling(statement,parm,mode):
    if(mode=="get"):
       try:
            # statement = "select * FROM `team141`.polls_data where ID_Question=5;"
            if(parm is not None):
                 db_cursor.execute(statement,parm)
            else:
                db_cursor.execute(statement)
            result=db_cursor.fetchall()
            return result

       except Exception as e:
            # print(e)
            return None

    if(mode=="update"):
        try:
            # statement = "select * FROM `team141`.polls_data where ID_Question=5;"
            if(parm is not None):
                db_cursor.execute(statement, parm)
            else:
                db_cursor.execute(statement)
            mydb.commit()
            return 1

        except Exception as e:
            # print(e)
            return None

if __name__ == "__main__":
    main()
