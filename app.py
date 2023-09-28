from flask import Flask, render_template, request
import base64
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission here
        username = request.form['username']
        password = request.form['password']
        workspace = request.form['workspace']
        repository = request.form['repository']
        commitFromDate = request.form['fromDate']
        commitToDate = request.form['toDate']

        startDate = datetime.strptime(commitFromDate, '%Y-%m-%d').date()
        endDate = datetime.strptime(commitToDate, '%Y-%m-%d').date()
 
        token = getBase64Encoding(username, password)

        commits = fetchCommitData(token, workspace, repository, startDate, endDate)

        commitDict = []

        for commit in commits:
            commitExists = False
            print(f'authod name {commit["author"]["user"]["display_name"]}')
            for data in commitDict:
                if data["name"] == commit["author"]["user"]["display_name"]:
                    data["count"] += 1
                    commitExists = True
                    break
            
            if not commitExists:
                firstData = {
                    "name" : commit["author"]["user"]["display_name"],
                    "count" : 1
                }
                commitDict.append(firstData)

        return render_template('result.html', objects=commitDict)       
        

    return render_template('index.html')


# Encode the string to Base64
def getBase64Encoding(username, password):
    stringToEncode = username+":"+password
    encoded_bytes = base64.b64encode(stringToEncode.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')

    return encoded_string

def fetchCommitData(token, workspace, repository, startDate, endDate):
    baseUrl = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repository}/commits"
    return fetchCommits(baseUrl, token, startDate, endDate)

def fetchCommits(url, token, startDate, endDate):
    commitsBetweenDates = []
    while url:
        response = requests.get(url,
                                headers={
                                    'Accept': 'application/json',
                                    'Authorization': 'Basic '+token
                                })
        if response.status_code == 200:
            commits = response.json()['values']
            
            for commit in commits:
                commitDate = commit['date']
                splitedDate = commitDate.split("T")
                commitDate = datetime.strptime(splitedDate[0], "%Y-%m-%d").date()

                if endDate <= commitDate <= startDate:
                    commitsBetweenDates.append(commit)
                    

            if commitDate < startDate:
                print('formatted date is ',commitDate)
                break
            
            next_page_url = response.json().get('next')
            print(f'next_page_url {next_page_url}')
            if next_page_url:
                    url = next_page_url
            else:
                break
    
    return commitsBetweenDates


if __name__ == '__main__':
    app.run(debug=True)
