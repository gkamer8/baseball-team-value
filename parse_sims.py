import json

if __name__ == "__main__":
    
    filename = "Sim Records/v1.json"
    sim = json.load(open(filename))

    team_records = sim['teams']