
# import sqlite3
import requests
import json
import config
import pickle

scores_user1 = []
scores_user2 = []
scores_user3 = []

for x in range (1,13):
    scores_api = requests.get('https://new.scoresaber.com/api/player/' + config.users[0][0] + '/scores/recent/' + str(x))
    scores_user1 += scores_api.json()["scores"]
    
for x in range (1,21):
    scores_api = requests.get('https://new.scoresaber.com/api/player/' + config.users[1][0] + '/scores/recent/' + str(x))
    scores_user2 += scores_api.json()["scores"]
    
for x in range (1,5):
    scores_api = requests.get('https://new.scoresaber.com/api/player/' + config.users[2][0] + '/scores/recent/' + str(x))
    scores_user3 += scores_api.json()["scores"]
    
with open('scores_user1.pickle', 'wb') as f:
    pickle.dump(scores_user1, f, pickle.HIGHEST_PROTOCOL)
    
with open('scores_user2.pickle', 'wb') as f:
    pickle.dump(scores_user2, f, pickle.HIGHEST_PROTOCOL)
    
with open('scores_user3.pickle', 'wb') as f:
    pickle.dump(scores_user3, f, pickle.HIGHEST_PROTOCOL)
