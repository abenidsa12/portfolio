import yaml

with open('static/data/info.yaml') as f:
    try:
        data = yaml.safe_load(f)
        print("Loaded\n", data['skills'])
        for content in data['social_media']:
            print("Loaded\n", data['social_media'][content])
        
        
    except yaml.YAMLError as e:
        print(e)