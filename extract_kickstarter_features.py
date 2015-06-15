import re
import json


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

    return [n_rewards, min_reward, max_reward, rewards_json, shipping_json, intn_ship]
