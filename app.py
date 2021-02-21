import ast
import os


import queries

import flask
from flask import Flask, jsonify, request,abort
app=Flask(__name__)


import configparser
my_config_parser = configparser.ConfigParser()
my_config_parser.read('config.ini')


port = my_config_parser.get('DEFAULT','port')
host = my_config_parser.get('DEFAULT','host')



# convert dic expression to dic
def convExprToDict(expression):
  dict=[]
  for x in expression:
        dict.append(ast.literal_eval(x[0]))
  return dict


@app.route('/')
def index():
    return 'hello!'

# get info about worldwide
@app.route('/covid19/all')
def get_forAll():
    exp_all=queries.worldWideData()
    if(exp_all is None):
        abort(404)
    else:
        all=convExprToDict(exp_all)
        dict1=all[0]
        # the position
        dict1["lat"]=34.80746
        dict1["long"]=-40.4796
        return jsonify(all)

# get info about one country
@app.route('/covid19/<countryId>')
def get_country(countryId):
    # get info from the db
    id=int(countryId)
    exp_country=queries.countryData(id)
    if(exp_country is None):
        abort(404)
    else:
        country=convExprToDict(exp_country)
        return jsonify(country)


# get info about each country,include lands
@app.route('/covid19/countries')
def get_countries():
    # get info from the db, value -can be the id of the country
    exp_countries=queries.countriesData()
    if(exp_countries is None):
        abort(404)
    else:
        countries=convExprToDict(exp_countries)
        return jsonify(countries)

# get info about each country sorted
@app.route('/covid19/countries/sorted')
def get_countriesSorted():
    # get info from the db,all the cases till now of each country
    exp_countries=queries.countriesSorted()
    if(exp_countries is None):
        abort(404)
    else:
        countries=convExprToDict(exp_countries)
        return jsonify(countries)

# get historical info in days
@app.route('/covid19/historical/all/<numDays>,<case>')
def get_historicalAll(numDays,case):
    # if(case!='cases' and case!='deaths'):
    #     return jsonify("worng input!no case like this!")
    # get info from the db,all the cases till now of each country
    exp_history=queries.historyInfo(numDays,case)
    if(exp_history is None):
        abort(404)
    else:
        history=convExprToDict(exp_history)
        # print(exp_history)
        return jsonify(history)

# return the active polls only
@app.route('/ActivePolls')
def get_active_polls():
    # need to return only the active
    exp_active_polls=queries.activePolls()
    if(exp_active_polls is None):
        abort(404)
    else:
        active_polls=convExprToDict(exp_active_polls)
        num = len(active_polls)
        result = {"polls": active_polls, "num": num}
        return result


# update poll, add 1 to counter of yes or no
@app.route('/polls/counter/<id>,<answer>',methods=['PUT'])
def update_poll(id,answer):
    # send the db request to update the id
    index=int(id)
    check=queries.updatePollCount(index,answer)
    if(check is None):
        abort(404)
    else:
        if check==1:
            return jsonify("succed update")
        else:
            return jsonify("failed updating")


# return mainlands sorted in desc order by cases
@app.route('/covid19/mainlandsSorted')
def get_mainlandSorted():
    exp_mainlands=queries.mainlandSorted()
    if(exp_mainlands is None):
        abort(404)
    else:
        mainlands=convExprToDict(exp_mainlands)
        return jsonify(mainlands)


# get true of false for password and user
@app.route('/Mangaer',methods=['PUT'])
def check_user():
    user=request.json['user']
    password=request.json['password']
    # check if the user exsits
    bool=queries.checkLogin(user,password)
    if(bool is None):
        abort(404)
    else:
        if bool:
            check=True
        else:
            check=False
        return jsonify(check)

# get all the polls from the db
@app.route('/polls')
def get_polls():
    exp_polls=queries.allPolls()
    if(exp_polls is None):
        abort(404)
    else:
        polls=convExprToDict(exp_polls)
        return jsonify(polls)

# add new poll-func 10
@app.route('/polls/<qes>',methods=['POST'])
def add_poll(qes):
    q=request.json['qes']
    # add new poll to db and get his id
    new_id=queries.addPoll(q)
    if(new_id is None):
        abort(404)
    else:
        # return the new item
        item = {"id": new_id, "title": q, "mode": 0, "yes": 0, "no": 0}
        return jsonify(item)

# update poll, make him hide or show ,true is show
@app.route('/polls/mode/<id>,<mode>',methods=['PUT'])
def update_mode_poll(id,mode):
    if(mode=='true'or mode=='True'):
        mode=True
    else:
        mode=False
    index=int(id)
    # update the poll in db ,1-means show,0-means hide
    check=queries.updatePollMode(mode,index)
    if(check is None):
        abort(404)
    else:
        if check==1:
            return jsonify("succed update")
        else:
            return jsonify("the same value,nothing change!")

# delete poll
@app.route('/polls/<id>',methods=['DELETE'])
def delete_poll(id):
    index=int(id)
    check=queries.deletePoll(index)
    if(check is None):
        abort(404)
    else:
        if check == 1:
            return jsonify("succed deleting")
        return jsonify("failed deleting")

# return the data for graph -given days back and the contury
@app.route('/covid19/Graphs/finance/<num_back>,<id_country>')
def get_financeGraphData(num_back,id_country):
    exp_graphData=queries.financeGraph(num_back,id_country)
    if(exp_graphData is None):
        abort(404)
    else:
        graphData=convExprToDict(exp_graphData)
        return jsonify(graphData)


# return the data for graph -given days back and the contury in proportion
@app.route('/covid19/Graphs/finance/prop/<num_back>,<id_country>')
def get_financeGraphDataProp(num_back, id_country):
    exp_graphData = queries.financeGraphProp(num_back, id_country)
    if (exp_graphData is None):
        abort(404)
    else:
        graphData = convExprToDict(exp_graphData)
        return jsonify(graphData)


# return the data for graph -given days back
@app.route('/covid19/Graphs/material/<num_back>')
def get_materialGraphData(num_back):
    exp_graphData = queries.materialGraph(num_back)
    if(exp_graphData is None):
        abort(404)
    else:
        graphData = convExprToDict(exp_graphData)
        return jsonify(graphData)


# return the data for graph -given days back in proporstion
@app.route('/covid19/Graphs/material/prop/<num_back>')
def get_materialGraphDataProp(num_back):
    exp_graphData=queries.materialGraphProp(num_back)
    if(exp_graphData is None):
        abort(404)
    else:
        graphData = convExprToDict(exp_graphData)
        return jsonify(graphData)


# return the countries of finance graph
@app.route('/covid19/Graphs/finance/countries')
def get_financeCountries():
    exp_countries =queries.countriesFinance()
    if(exp_countries is None):
        abort(404)
    else:
        countries = convExprToDict(exp_countries)
        return jsonify(countries)


if __name__ == "__main__":
    app.run(host=host, port=port)



