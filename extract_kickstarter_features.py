import re
import json
import time
import datetime
import numpy as np
from bs4 import BeautifulSoup
import pymysql as mdb

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
    median_reward = int(np.median(reward_int_list))
    max_reward = max(reward_int_list)
    #rewards_json = json.dumps(reward_int_list) 

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

    return n_rewards, min_reward,median_reward, max_reward, intn_ship, shipping_json

def get_time_features(unix_t_start):
    # weekdays are index 0=Monday
    # just truncate hour (0-23) for now; ignore minutes

    t_struct = time.localtime(unix_t_start)  

    # month, day of month, day of week, hour
    return [t_struct.tm_mon, t_struct.tm_mday, t_struct.tm_wday, t_struct.tm_hour] 

def calc_days_to_ship(rewards_ship_dates_str,campaign_start_unix_t):
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
                        'Dec':12,\
                        'December':12} #hack

    # convert all rewards_ship_dates
    for i, ship_d_str in enumerate(rewards_ship_dates):
        month_str, year_str = ship_d_str.split()

        month_int = month_str_to_int[month_str]
        year_int = int(year_str)

        dt = datetime.datetime(year_int, month_int, 1) #assume day 1
        ship_ts_unix_t[i] = time.mktime(dt.utctimetuple())

    # get mode ship time
    min_ship_unix_t = np.median(ship_ts_unix_t)

    s_to_ship = min_ship_unix_t - campaign_start_unix_t
    # if negative, convert to 0. 
    if s_to_ship < 0:
        s_to_ship = 0

    s_per_day = 86400

    days_to_ship = int(round(float(s_to_ship)/s_per_day))
    return days_to_ship

def analyze_description_features(soup,text):
    #soup = BeautifulSoup(project_html)
    #


    text = soup.get_text()

    # counds of external links, figures, videos
   
    n_links = 0
    for link in soup.find_all('a'):
        if not link.get('href') is None:
            if link.get('href').startswith('http'):
                n_links = n_links + 1

    n_figs = len(soup.find_all('figure'))

    # analyze body text ________________________________
    # find the index of Kickstarter's have a question
    end_body_i = -1
    for end_body in re.finditer('Have a question\?\nIf the info above doesn\'t help, you can ask the project creator directly',text):
        end_body_i = end_body.start()
    
    if end_body_i == -1:
        for end_body in re.finditer('Report this project to Kickstarter',text):
            end_body_i = end_body.start()
   
    #if end_body_i == -1:
    #    print 'no body end found'


    if end_body_i == -1:
        body_n_words = len(text.split())
    else:
        body_n_words = len(text[:end_body_i].split())

    return n_links, n_figs, body_n_words
    




    # inconsistent format for faq and risks.  -- later just pick time ranges with the same format.

    # risk_start_i = -1
    # # find the index of Kickstarter's risks
    # risk_str = 'Risks and challenges'
    # for risk in re.finditer(risk_str,text):
    #     risk_start_i = risk.start()+len(risk_str)
    
    # faq_start_i = -1
    # # find the index of Kickstarter's FAQ
    # faq_str = 'FAQ'
    # for faq in re.finditer(faq_str,text):
    #     #if faq_start_i == -1: # only assign on first. there must be a better way to do this.
    #         faq_start_i = faq.start()+3
    
    # if risk_start_i == -1:
    #     risks_n_words = 0
    # else:
    #     risks_n_words = len(text[risk_start_i:faq_start_i-3].split())
    
    # if faq_start_i == -1:
    #     faq_n_words = 0
    # else:
    #     #print text[faq_start_i:end_body_i]
    #     faq_n_words = len(text[faq_start_i:end_body_i].split())

def concat_features(primary_key):
    con = mdb.connect('localhost','root','hobbes','kickstarter')

    project_features = get_project_features(con,primary_key)
    body_features = get_body_features(con,primary_key,project_features[10])
    creator_features = get_creator_features(con,primary_key)

    return project_features + body_features + creator_features

def get_project_features(con,primary_key):
    # primary_key_id 0
    # url 1
    # outcome 2
    # pledged 3
    # goal 4
    # category 5
    # subcategory 6
    # currency 7
    # country 8
    # location 9
    # launch time 10
    # campaign dur
    # title_n_words
    # blurb_n_words
    # Month INT,\
    # Monday_day INT,\
    # Week_day INT,\
    # Hour INT,\
    project_info = []
    
    with con:
        cur = con.cursor()
        cur.execute("SELECT Id,URL,Project_date,Pledged,Goal,Category_name,Category_slug,Currency,\
                         Country,Location_club,Launch_time from Project_info WHERE Id = %s",primary_key)
        rows = cur.fetchall()
        project_info_pt1 = list(rows[0])
        
        cur.execute("SELECT Launch_time,End_time,Name,Blurb from Project_info WHERE Id = %s",primary_key)
        rows = cur.fetchall()
        start_t,end_t,name,blurb = rows[0]
        cur.close()
        
        # a little processing for duration, title words, blurb words
        s_per_day = 86400
        campaign_dur = int(round(float(end_t-start_t)/s_per_day))
        title_n_words = len(name.split())
        blurb_n_words = len(blurb.split())
        
        # now add time info
        time_info = get_time_features(start_t)
        
        project_info = project_info_pt1 + [campaign_dur,title_n_words,blurb_n_words] + time_info
        
        
    return project_info
        
def get_body_features(con,primary_key,launch_s):
    # N_rewards INT,\
    # Min_reward INT,\
    # Median_reward INT,\
    # Max_reward BIGINT,\
    # Reward_ship_days INT,\
    # Ships_intn TINYINT,\
    # N_links INT,\
    # N_figs INT,\
    # Body_n_words INT,\
    
    body_features = []
    with con:
        cur = con.cursor()
        cur.execute("SELECT Project_html from Scraped_pages WHERE Id = %s",primary_key)
        retrieved_text = cur.fetchall()
        cur.close()
    
        project_html = retrieved_text[0][0]
        this_soup = BeautifulSoup(project_html)
        project_text = this_soup.get_text()
        n_rewards, min_reward, median_reward, \
            max_reward, intn_ship, shipping_json = analyze_rewards(project_text)
            
        days_to_ship = calc_days_to_ship(shipping_json,launch_s)
        
        reward_info = [n_rewards,min_reward,median_reward,max_reward,days_to_ship,intn_ship]
        n_links, n_figs, body_n_words = analyze_description_features(this_soup,project_text)
        
        desc_features = [n_links,n_figs,body_n_words]
        
        body_features = reward_info + desc_features
    return body_features

def get_creator_features(con,primary_key):
    #N_creator_backed INT
    with con:
        cur = con.cursor()
        cur.execute("SELECT Creator_html from Scraped_pages WHERE Id = %s",primary_key)
        retrieved_text = cur.fetchall()
        cur.close()

        this_soup = BeautifulSoup(retrieved_text[0][0])
        creator_text = this_soup.get_text()
        n_backed = get_creator_activity(creator_text)

        return [n_backed]
