import re
import json
import time
import datetime
import numpy as np
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode


def live_scrape_page(url):
# make this robust
    project_url = url + '/description'
    creator_url = url + '/creator_bio'

    project_request = requests.get(project_url)
    project_raw = unidecode(project_request.text)

    creator_request = requests.get(creator_url)
    creator_raw = unidecode(creator_request.text)

    n_backed = get_creator_activity(creator_raw)
    body_features = analyze_description_features(project_raw)

    print n_backed
    print body_features


def get_creator_activity(creator_html):
    soup = BeautifulSoup(creator_html)
    text = soup.get_text()

    # initialize for -1 so I can see where my parsing failed
    n_backed = -1
    
    # get number of campaigns backed
    match = re.search(r'Backed\n\((\d+)\)',text)
    if match:
        n_backed = int(match.group(1))
     

    return n_backed


def analyze_rewards(project_text):

    # extract reward levels! -- this isn't robust to other currencies or commas
    matches = re.findall('[\$\w+](\d+,*\d*) reward',project_text)
    #matches = re.findall('\$(\d+) reward',project_text) 
    if matches:    
        reward_int_list = [int(match.replace(',','')) for match in matches]
        n_rewards = len(reward_int_list)
    else:
        reward_int_list = [-1]
        n_rewards = len(reward_int_list)

    # now get reward summaries
    n_rewards = len(reward_int_list)
    min_reward = min(reward_int_list)
    median_reward = int(np.median(reward_int_list))
    max_reward = max(reward_int_list)
    #rewards_json = json.dumps(reward_int_list) 

    # look for international shipping   
    match = re.search(r'Ships anywhere in the world',project_text)
    if match:
        intn_ship = 1
    else: 
        intn_ship = 0
        
    return n_rewards, min_reward,median_reward, max_reward, intn_ship

def analyze_description_features(project_html):
    soup = BeautifulSoup(project_html)
    text = soup.get_text()

    body_n_words = -1
    goal = -1
    category = '-1'

    # get rewards info ________________________________
    n_rewards,min_reward,median_reward, max_reward,intn_ship = analyze_rewards(text)

    # analyze category _________________________________
    # this gets categories
    match = re.search('categories/(\w+)/',project_html)
    if match:
        category = match.group(1)

    # analyze goals ____________________________________
    match = re.search('(\d+,*\d+) goal',text)
    if match:
        goal_str = match.group(1)
        goal = int(goal_str.replace(',',''))


    # analyze body text ________________________________
    # find the index of Kickstarter's have a question
    end_body_i = -1
    for end_body in re.finditer('Have a question\?\nIf the info above doesn\'t help, you can ask the project creator directly',text):
        end_body_i = end_body.start()
    
    if end_body_i == -1:
        for end_body in re.finditer('Report this project to Kickstarter',text):
            end_body_i = end_body.start()
   
    if end_body_i == -1:
        body_n_words = len(text.split())
    else:
        body_n_words = len(text[:end_body_i].split())

    return [category,goal,body_n_words,n_rewards,min_reward,median_reward, max_reward,intn_ship]
    

