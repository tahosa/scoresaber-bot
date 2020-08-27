import pickle
import requests
import json
import config
import time
import discord
import asyncio
from discord.ext import tasks, commands
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)

client = discord.Client()



# with open('user_scores.pickle', 'rb') as f:
    # user_scores = pickle.load(f)
    
    
with open('scores_user1.pickle', 'rb') as f:
    scores_user1 = pickle.load(f)
    
with open('scores_user2.pickle', 'rb') as f:
    scores_user2 = pickle.load(f)
    
with open('scores_user3.pickle', 'rb') as f:
    scores_user3 = pickle.load(f)
    
# for testing
with open('1.json') as json_file:
    json1 = json.load(json_file)
    testjson = json1["scores"][0]
    # print (type(testjson))
    
    

    
    
async def compare_other_users(new_song_dict, inputdict):

    returnlist = []

    new_songhash = new_song_dict["songHash"]
    new_songdiff = new_song_dict["difficulty"]
    new_songscore = new_song_dict["score"]
    # new_songname = new_song_dict["songName"] + " " + new_song_dict["songSubName"]
    new_songdiffraw = new_song_dict["difficultyRaw"].split("_")[1]
    new_songAuthorName = new_song_dict["songAuthorName"]
    new_levelAuthorName = new_song_dict["levelAuthorName"]
    
    # formatting
    if new_song_dict["songSubName"] == "":
        new_songname = new_song_dict["songName"]
    else:
        new_songname = new_song_dict["songName"] + " " + new_song_dict["songSubName"]
        
    if new_songAuthorName == "":
        new_songby = new_levelAuthorName
    elif new_levelAuthorName == "":
        new_songby = new_songAuthorName
    else:
        new_songby = new_songAuthorName + " / " + new_levelAuthorName
    
    ### Paul ###
    
    if inputdict == scores_user1:
        oldscore = next((item.get('score') for item in scores_user1 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        comparescore = next((item.get('score') for item in scores_user2 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        if comparescore == False:
            print ("Wil has not played this song")
        else:
            # print (oldscore)
            # print (comparescore)
            # print (new_songscore)
            if oldscore <= comparescore:
                if new_songscore >= comparescore:
                    returnlist += ("Paul just got a score of " + str(new_songscore) + " in " + str(new_songname) + " by " + new_songby + " on " + str(new_songdiffraw) + ", beating Wil's score of " + str(comparescore)) + ". "
                else:
                    print ("Wil is still beating Paul")
            else:
                print ("Paul was already beating Wil")
                
        comparescore = next((item.get('score') for item in scores_user3 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        if comparescore == False:
            print ("Momo has not played this song")
        else:
            # print (comparescore)
            # print (new_songscore)
            if oldscore <= comparescore:
                if new_songscore >= comparescore:
                    returnlist += ("Paul just got a score of " + str(new_songscore) + " in " + str(new_songname)+ " by " + new_songby +  " on " + str(new_songdiffraw) + ", beating Momo's score of " + str(comparescore)) + ". "
                else:
                    print ("Wil is still beating Paul")
            else:
                print ("Paul was already beating Momo")
                
    ### Wil ###
    
    elif inputdict == scores_user2:
        oldscore = next((item.get('score') for item in scores_user2 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        comparescore = next((item.get('score') for item in scores_user1 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        if comparescore == False:
            print ("Paul has not played this song")
        else:
            # print (comparescore)
            # print (new_songscore)
            if oldscore <= comparescore:
                if new_songscore >= comparescore:
                    returnlist += ("Wil just got a score of " + str(new_songscore) + " in " + str(new_songname) +  " by " + new_songby + " on " + str(new_songdiffraw) + ", beating Paul's score of " + str(comparescore)) + ". "
                else:
                    print ("Paul is still beating Wil")
            else:
                print ("Wil was already beating Paul")
                
        comparescore = next((item.get('score') for item in scores_user3 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        if comparescore == False:
            print ("Momo has not played this song")
        else:
            # print (comparescore)
            # print (new_songscore)
            if oldscore <= comparescore:
                if new_songscore >= comparescore:
                    returnlist += ("Wil just got a score of " + str(new_songscore) + " in " + str(new_songname) + " by " + new_songby +  " on " + str(new_songdiffraw) + ", beating Momo's score of " + str(comparescore)) + ". "
                else:
                    print ("Paul is still beating Wil")
            else:
                print ("Wil was already beating Momo")
                
    ### Momo ###
    
    elif inputdict == scores_user3:
        oldscore = next((item.get('score') for item in scores_user3 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        comparescore = next((item.get('score') for item in scores_user1 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        if comparescore == False:
            print ("Paul has not played this song")
        else:
            # print (comparescore)
            # print (new_songscore)
            if oldscore <= comparescore:
                if new_songscore >= comparescore:
                    returnlist += ("Momo just got a score of " + str(new_songscore) + " in " + str(new_songname) + " by " + new_songby +  " on " + str(new_songdiffraw) + ", beating Paul's score of " + str(comparescore)) + ". "
                else:
                    print ("Paul is still beating Momo")
            else:
                print ("Momo was already beating Paul")
                
        comparescore = next((item.get('score') for item in scores_user2 if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), False)
        if comparescore == False:
            print ("Wil has not played this song")
        else:
            # print (comparescore)
            # print (new_songscore)
            if oldscore <= comparescore:
                if new_songscore >= comparescore:
                    returnlist += ("Momo just got a score of " + str(new_songscore) + " in " + str(new_songname)+  " by " + new_songby + " on " + str(new_songdiffraw) + ", beating Wil's score of " + str(comparescore)) + ". "
                else:
                    print ("Wil is still beating Momo")
            else:
                print ("Momo was already beating Wil")
                
    if returnlist == []:
        return None
    else:
        returnmsg = ''.join(returnlist)
        return returnmsg
    
# print (search('1CA47694DE9471BA8D855AC776AFF36C4321A521', scores_user1, 7))

async def find_and_replace_song(new_song_dict, scoreslistdict, user):
    # finds the index of a song given the songhash and difficulty
    new_songhash = new_song_dict["songHash"]
    new_songdiff = new_song_dict["difficulty"]
    new_songscore = new_song_dict["score"]
    list_index = next((i for i, item in enumerate(scoreslistdict) if (item["songHash"] == new_songhash) and (item['difficulty'] == new_songdiff)), None)
    if list_index == None:
        # print ("New song")
        # print (new_song_dict)
        # print (type(new_song_dict))
        # check to see if they beat any of the other users scores
        result =  await compare_other_users(new_song_dict, scoreslistdict)
        # add the new song to the list
        scoreslistdict.append(new_song_dict.copy())
        with open('scores_' + user + '.pickle', 'wb') as f:
            pickle.dump(scoreslistdict, f, pickle.HIGHEST_PROTOCOL)
        return result
    else:
        old_score = scoreslistdict[list_index]['score']
        if new_songscore > old_score:
            # check to see if they beat any of the other users scores
            result =  await compare_other_users(new_song_dict, scoreslistdict)
            # replace their old score with the new one
            scoreslistdict[list_index]['score'] = new_songscore
            with open('scores_' + user + '.pickle', 'wb') as f:
                pickle.dump(scoreslistdict, f, pickle.HIGHEST_PROTOCOL)
            return result
        else:
            # print (user + " No new scores")
            return None
            
# find_and_replace_song(testjson, scores_user2)

# find_and_replace_song('1CA47694DE9471BA8D855AC776AFF36C4321A521', 7, 11111111, scores_user1)
    
# print(json1["scores"][0])
    
# print (scores_user1)

# findsong = next((item.get('score') for item in scores_user1 if (item["songHash"] == "45511701D2D643984EB6E9637889B335A7B26854") and (item['difficulty'] == 5)), False) 

new_scores_user1 = []
new_scores_user2 = []
new_scores_user3 = []

'''
# every minute, get the new scores
starttime = time.time()
while True:
    print ("tick")
    
    # scores_api = requests.get('https://new.scoresaber.com/api/player/' + config.users[0][0] + '/scores/recent/1')
    # scores_api = requests.get(1.json)
    new_scores_user1 = testjson
    if new_scores_user1 == scores_user1[0]:
        print ("Same scores")
    else:
        # find the old score and replace it
        print ("Different")
        find_and_replace_song(new_scores_user1, scores_user1)
        
        
        
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))

# print (findsong)
'''

    

# print (search('1CA47694DE9471BA8D855AC776AFF36C4321A521', scores_user2, 7)[0]['score'])

@tasks.loop(seconds=60.0)
async def printer():
    # print("getting scores")
    # channel = client.get_channel(481172020051312660)
    channel = client.get_channel(710949678447067256)
    # await channel.send('Hello!')
    async with aiohttp.ClientSession() as session:
        async with session.get('https://new.scoresaber.com/api/player/' + config.users[0][0] + '/scores/recent/1') as r:
            # print (r.status)
            if r.status == 200:
                js = await r.json()
                # print (js['scores'][0]['score'])
                beatmsg = await find_and_replace_song(js['scores'][0], scores_user1, 'user1')
                # print(testjson)
                # beatmsg = await find_and_replace_song(testjson, scores_user1, 'user1') #for testing
                # print(testjson)
                if beatmsg != None:
                    print (beatmsg)
                    await channel.send(str(beatmsg))
                    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://new.scoresaber.com/api/player/' + config.users[1][0] + '/scores/recent/1') as r:
            # print (r.status)
            if r.status == 200:
                js = await r.json()
                # print (js['scores'][0]['score'])
                beatmsg = await find_and_replace_song(js['scores'][0], scores_user2, 'user2')
                if beatmsg != None:
                    print (beatmsg)
                    await channel.send(str(beatmsg))
                    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://new.scoresaber.com/api/player/' + config.users[2][0] + '/scores/recent/1') as r:
            # print (r.status)
            if r.status == 200:
                js = await r.json()
                # print (js['scores'][0]['score'])
                beatmsg = await find_and_replace_song(js['scores'][0], scores_user3, 'user3')
                if beatmsg != None:
                    print (beatmsg)
                    await channel.send(str(beatmsg))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('hello bot'):
        await message.channel.send('Hewwo uwu')
        

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    printer.start()


client.run(config.discord_bot_token)
