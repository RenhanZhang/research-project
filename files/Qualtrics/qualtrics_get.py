import os
import ipdb
import urllib
import json
from DB_Handling import BlogsDB
from datetime import datetime, date, timedelta
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

# retrieve new response data from Qualtrics, may setup last_retrieved mechanism in the future
def get_new_legacy(survey_id):
    #ipdb.set_trace()
    account = read_account()
    url = BASE_URL + '?%s'
    # all the parameters 
    params = {'Request': 'getLegacyResponseData', 'User': account['id'], \
              'Token': account['token'], 'Format': 'JSON', \
              'SurveyID': survey_id, 'Version': '2.0'}
    
    # check if the file recording the lastResponseID exists
    fname = dirname + '/lastResponseID/' + survey_id
    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            s = f.read().strip()
            if len(s) > 0:
                params['LastResponseID'] = s    
    
    # ipdb.set_trace()
    params = urllib.urlencode(params)
    result = json.loads((urllib.urlopen(url % params)).read())
    
    if len(result) > 0:
        with open(fname, 'w') as f:
            last_response_id = sorted(result.items(), key=lambda x: x[1]['EndDate'], reverse=True)[0][0]
            f.write(last_response_id)
    return result

# get profile url based on token
def get_profile_by_token(token, dbh):
    # search the profile url based on the token
    stmt = 'select profile_url from profiles_tokens where token = %s;'
    result = dbh.exec_and_get(stmt, [token])
    assert len(result) == 1
    return result[0][0]

# update the profiles_surveys table in the database for a certain survey
# by retrieving all the new data from the last retrieved data
def update_profiles_surveys(survey_id, survey_name, id_col='Token', dbh=None):
    new_records = get_new_legacy(survey_id)
    #ipdb.set_trace()
    if not dbh:
        dbh = BlogsDB.BlogsDB_Handler()

    for response in new_records:
        details = new_records[response]
        token = details[id_col]
        profile_url = get_profile_by_token(token, dbh) 
        
        # update the profiles_surveys table
        stmt = 'insert ignore into profiles_surveys(profile_url, survey_id) values(%s, %s);'
        dbh.exec_stmt(stmt, [profile_url, survey_id])
        
        # if it's the big-5 survey, also update the big_5_from_survey table in db
        if survey_name == 'big-5':
            stmt = 'insert into big_5_from_survey values(%s, %s, %s, %s, %s, %s)'
            params = [profile_url, float(details['Extraversion']), float(details['Agreeableness']),\
                      float(details['Conscientiousness']), float(details['Neuroticism']), float(details['Openness'])]
            dbh.exec_stmt(stmt, params)

# retrieve all survey participants in a survey
# the id_col arg is the name of the question of the survey that uniquely identifies
# the respondents (the token that we assigned to blogger writers). 
def get_respondents(survey_id, id_col='Token'):
    
    data = get_legacy(survey_id)
    respondents = []
    for response in data:
        respondents.append(data[response][id_col])

    return respondents

# check if a profile has taken the survey by looking up the table
def have_taken(profile_url, survey_id, dbh):
    stmt = 'select * from profiles_surveys where profile_url = %s and survey_id = %s;'
    result = dbh.exec_and_get(stmt, [profile_url, survey_id])

    assert len(result) < 2

    if len(result) == 0:
        return False
    else:
        return True

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
        update_profiles_surveys(survey_id, surveys[survey_id], id_col='Token', dbh=dbh)
        if have_taken(profile_url, survey_id, dbh): 
            result.append(surveys[survey_id])
    return result
         
# get_legacy('SV_5jdQJNC0LxIdvc9')
