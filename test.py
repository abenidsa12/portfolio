import yaml

with open('static/data/info.yaml') as f:
    try:
        data = yaml.safe_load(f)
        print("Loaded\n", data['skills'])
        print("Loaded\n", data['certifications']['name'])
        
        
    except yaml.YAMLError as e:
        print(e)