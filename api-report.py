import requests
import csv
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
############################### SETTINGS ######################################
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
            "Caccia_al_tesoro"]
###############################################################################

def main( ) :
    headers = list(TASKS)
    headers.insert(0, "Username")

    users = loadUsers(USERS_FILENAME)
    results = fetchAllData(users)
    storeResults(RESULTS_FILENAME, results, headers)

def fetchAllData( users ):
    results = []
    count = len(users)
    for i,u in enumerate(users):
        # print "Username: " + u[0] + " || Password: " + u[3]
        session = signIn(u[0], u[3])
        # print "COOKIE: " + str(session)
        r = fetchResults(session, TASKS)
        r.update({'Username' : u[0]})
        results.append(r)
        print str(i + 1) + "/" + str(count) + " done..."
        #print "User <" + u[0] + "> completed!"
    return results

def fetchResults( session, tasks ):
    results = {}
    for t in tasks:
        r = requests.get(TASK_URL(t), cookies=session)
        results.update({t : fetchLatestResult(r.text)})
    return results

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
    return score.text[1:-1].encode("utf-8")

def signIn( username, password ):
    payload = {'next': '/', 'username': username, 'password': password}
    r = requests.post(LOGIN_URL, data = payload)
    cookies = r.cookies;
    return cookies

def loadUsers( filename ):
    with open('users.csv', 'rb') as f:
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

main()
