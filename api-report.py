import csv
import requests
import argparse

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

########################### DEFAULT SETTINGS ##################################
USERS_FILENAME = "users.csv"
RESULTS_FILENAME = "results.csv"
BASE_URL  = "https://dum-e.deib.polimi.it"
LOGIN_URL = BASE_URL + "/login"
TASK_URL = lambda name: BASE_URL + "/tasks/" + name + "/submissions"
TASKS = [   "Tutorial",
            "Semplice",
            "Cespuglio",
            "Liane",
            "Cactus",
            "Tiglio",
            "Potatura",
            "Caccia_al_tesoro" ]
###############################################################################

def main( ) :
    io = parameterHandler()

    headers = list(TASKS)
    headers.insert(0, "Username")

    users = loadUsers(io['in'])
    results = fetchingStrategy(users)
    storeResults(io['out'], results, headers)

def parameterHandler():
    global BASE_URL

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', help='Users csv file', required=False)
    parser.add_argument('-o','--output', help='Results csv file', required=False)
    parser.add_argument('-b','--base_url', help='The basic URL where the CMS is located', required=False)

    args = parser.parse_args()
    inputName = USERS_FILENAME
    outputName = RESULTS_FILENAME

    if args.input != None:
        inputName = args.input
    if args.output != None:
        outputName = args.output
    if args.base_url != None:
        BASE_URL = args.base_url

    return {'in' : inputName, 'out' : outputName}

''' WARNING:
    - fetchingStrategy: this method dramatically relies on the structure of the
                        csv file. It takes as input a list  of <USR_TUPLE> and
                        returns a dictionaries with the results for all
                        the users in the input list.

    <USR_TUPLE> : <Username, _, _, Password, _*> -> needed structure to work.
'''
def fetchingStrategy( users ):
    results = []
    count = len(users)
    for i,u in enumerate(users):
        session = signIn(u[0], u[3])
        r = fetchAllResults(session, TASKS)
        r.update({'Username' : u[0]})
        results.append(r)
        print str(i + 1) + "/" + str(count) + " done..."
    return results

def fetchAllResults( session, tasks ):
    results = {}
    for t in tasks:
        r = requests.get(TASK_URL(t), cookies=session)
        results.update({t : fetchLatestResult(r.text)})
    return results

''' Traversing the document tree:
    - fetchLatestResult:    strongly depends on the actual html structure we
                            are trying to parse.
                            Given an HTTP Response object, returns the list of
                            scores of the user.
'''
def fetchLatestResult( html ):
    doc = BeautifulSoup(html, "html.parser")
    table = doc.find('tbody')
    row = table.find('tr')
    #print row.text
    score = row.find('td', {"class" : "total_score"})
    if score == None:
        score = row.find('td', {"class" : "public_score"})
        if score == None:
            return "No Submissions"
    return score.text.strip().encode("utf-8")

def signIn( username, password ):
    payload = {'next': '/', 'username': username, 'password': password}
    r = requests.post(LOGIN_URL, data = payload)
    cookies = r.cookies;
    return cookies

''' Input management methods:
    - loadUsers:    loads the csv properly-formatted file and
                    returns it into a list of tuples
    - storeResults: stores the results list of dictionaries into a csv file
                    having the same structure as the dictionaries

    Note: these methods are csvs-structure invariant.
'''
def loadUsers( filename ):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        users = map(tuple, reader)
    return users

def storeResults( filename, results, headers ):
    with open(filename, 'wb') as f:
        w = csv.DictWriter(f, fieldnames = headers)
        w.writeheader()
        for i in results:
            w.writerow(i)
    print "Results stored correctly at: " + filename

'''
    PROGRAM EXECUTION:
'''
main()
