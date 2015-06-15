from unidecode import unidecode

def extract_project_info(project_json):

    creator_name = unidecode(project_json['creator']['name'])
    creator_url = project_json['creator']['urls']['web']['user']
    currency = unidecode(project_json['currency'])
    p_id = project_json['id']

    category_slug = unidecode(project_json['category']['slug'])
    category_name = unidecode(project_json['category']['name'])
    
    #time stamps -- I don't understand their formatting
    launch_time = project_json['launched_at'] 
    deadline = project_json['deadline']
    
    goal = project_json['goal']
    pledged = project_json['pledged']
    project_state = unidecode(project_json['state'])

    country = project_json['country']
    if 'location' in project_json:
        location_slub = project_json['location']['slug']
        location_name = unidecode(project_json['location']['displayable_name'])
    else:
        location_slub = ''
        location_name = ''
    
    
    blurb = unidecode(project_json['blurb'])
    n_backers = project_json['backers_count']
    name = unidecode(project_json['name'])


    url = project_json['urls']['web']['project']
    
    project_info = [creator_name,creator_url,currency,p_id,\
           category_name,category_slug,goal,\
           pledged,project_state,country,location_slub,\
           location_name,blurb,n_backers,name,url,\
                   launch_time, deadline]
    
    return project_info