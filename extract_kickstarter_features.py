import re
import json


import time
import datetime
import numpy as np
from scipy import stats

def get_creator_activity(creator_text_only):
    # initialize for -1 so I can see where my parsing failed
    n_backed = -1
    
    # get number of campaigns backed
    match = re.search(r'Backed\n\((\d+)\)',creator_text_only)
    if match:
        n_backed = int(match.group(1))
    
    # this also works    
    #match = re.search('is not backing any projects',creator_text_only)
         
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
    median_reward = median(reward_int_list)
    max_reward = max(reward_int_list)
    rewards_json = json.dumps(reward_int_list) 

    # look for international shipping   
    match = re.search(r'Ships anywhere in the world',project_text)
    if match:
        intn_ship = 1
    else: 
        match = re.search(r'Only ships to: United States',project_text)  
        if match:
            intn_ship = 0
        else: 
            intn_ship = -1 

    # get estimated delivery times  
    matches = re.findall('Estimated delivery:\n(\w+ \d+)',project_text)
    if matches:
        delivery_list = matches
    else:
        delivery_list = ['-1']
    shipping_json = json.dumps(delivery_list)

    return [n_rewards, min_reward,median_reward, max_reward, rewards_json, shipping_json, intn_ship]

def get_time_features(unix_t_start):
    # weekdays are index 0=Monday
    # just truncate hour (0-23) for now; ignore minutes

    t_struct = time.localtime(unix_t_start)  

    # month, day of month, day of week, hour
    return t_struct.tm_mon, t_struct.tm_mday, t_struct.tm_wday, t_struct.tm_hour 

def calc_days_to_reward(rewards_ship_dates_str,campaign_start_unix_t):
    # I think months to reward is more useful, but low roi. leave as is. 
    # convert to list
    rewards_ship_dates = json.loads(rewards_ship_dates_str)

    if rewards_ship_dates[0] == '-1':
        return -1

    ship_ts_unix_t = np.empty_like(rewards_ship_dates,dtype=int)

    month_str_to_int = {'Jan':1,\
                        'Feb':2,\
                        'Mar':3,\
                        'Apr':4,\
                        'May':5,\
                        'Jun':6,\
                        'Jul':7,\
                        'Aug':8,\
                        'Sep':9,\
                        'Oct':10,\
                        'Nov':11,\
                        'Dec':12}

    # convert all rewards_ship_dates
    for i, ship_d_str in enumerate(rewards_ship_dates):
        month_str, year_str = ship_d_str.split()

        month_int = month_str_to_int[month_str]
        year_int = int(year_str)

        dt = datetime.datetime(year_int, month_int, 1) #assume day 1
        ship_ts_unix_t[i] = time.mktime(dt.utctimetuple())

    # get mode ship time
    min_ship_unix_t = stats.mode(ship_ts_unix_t)

    s_to_ship = min_ship_unix_t - campaign_start_unix_t
    # if negative, convert to 0. 
    if s_to_ship < 0:
        s_to_ship = 0

    s_per_day = 86400

    days_to_ship = round(float(s_to_ship)/s_per_day)
    return days_to_ship

