import os
import ipdb
import urllib
import json
from DB_Handling import BlogsDB
dirname = os.path.dirname(os.path.abspath(__file__))
BASE_URL = 'https://survey.qualtrics.com/WRAPI/ControlPanel/api.php'
'''
?Request=getLegacyResponseData&User=user%40qualtrics.com&Token=jkf0AjdYXWU76B2kd0SifklbFOtoVPfXuhd9e274&Format=XML&Version=2.0&SurveyID=SV_cNsMvwobYEK3NT7&LastResponseID=R_6ExpflgVtDv38Hz&Limit=42&ResponseID=R_af8Zhnd3xR75Ky9&ResponseSetID=RS_3UfhTNybTd7kP4N&SubgroupID=SG_cVcw7rw67rsX1gV&StartDate=2015-10-10%2B08%253A36%253A40&EndDate=2015-10-10%2B08%253A36%253A40&Questions=String&Labels=1&ExportTags=1&ExportQuestionIDs=1&LocalTime=1&UnansweredRecode=42&PanelID=ML_af4BQyTW4IK0zuR&ResponsesInProgress=1&LocationData=1
'''
def read_account():
    with open('%s/account.txt' %dirname, 'r') as f:
         account = {}
         for line in f.readlines():
              tp = line.split('=')
              account[tp[0]] = tp[1].strip()
         return account

# retrieve all response data, may setup last_retrieved mechanism in the future
def get_legacy(survey_id):
    account = read_account()
    url = BASE_URL + '?%s'
    # all the parameters 
    params = urllib.urlencode({'Request': 'getLegacyResponseData', 'User': account['id'], \
                               'Token': account['token'], 'Format': 'JSON', \
                               'SurveyID': survey_id, 'Version': '2.0'})
    
    result = json.loads((urllib.urlopen(url % params)).read())
    return result

# retrieve all survey participants in a survey
# the id_col arg is the name of the question of the survey that uniquely identifies
# the respondents (the token that we assigned to blogger writers). 
def get_respondents(survey_id, id_col='Token'):
    
    data = get_legacy(survey_id)
    respondents = []
    for response in data:
        respondents.append(data[response][id_col])

    return respondents

def surveys_taken(profile_url):
    result = []
    dbh = BlogsDB.BlogsDB_Handler()

    # get the token for this profile from the db
    temp = dbh.exec_and_get('select token from profiles_tokens where profile_url=%s;', [profile_url])
    assert len(temp) == 1
    token = temp[0][0]

    # get a list of all surveys in the db
    surveys = {}         # key: survey_id, value: title
    for tp in dbh.exec_and_get('select title, qualtrics_id from surveys;', []):
        surveys[tp[1]] = tp[0]

    for survey_id in surveys:
        respondents = get_respondents(survey_id)
        if token in respondents:
            result.append(surveys[survey_id])

    return result
         
# get_legacy('SV_5jdQJNC0LxIdvc9')
