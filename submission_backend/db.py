from decimal import Decimal
import time
import boto3
from boto3.dynamodb.conditions import Key
import json

LOG_FILE = "database/evaluated_repos.json"

def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    else:
        return obj

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimals to floats
    raise TypeError ("Type not serializable")



class DBClient():
    def __init__(self, aws_access_key_id, aws_access_key_secret) -> None:
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_access_key_secret,
            region_name='ap-southeast-2'
        )

        dynamodb = self.session.resource('dynamodb')
    
        table_name = 'green-battery-hack'
        self.table = dynamodb.Table(table_name)
    
    def is_already_submitted(self, team, submission_hash):
        response = self.table.get_item(
            Key={
                'team': team,
                'commit_hash': submission_hash
            }
        )
        return 'Item' in response

    def submit(self, submission):
        assert 'team' in submission, f'team (primary key) not found in {submission}'
        assert 'commit_hash' in submission, f'commit_hash (secondary key) not found in {submission}'
        
        cloned_submission = convert_floats_to_decimal(submission.copy())
        cloned_submission['submitted_at'] = int(round(time.time() * 1000))

        response = self.table.put_item(Item=cloned_submission)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        
        print("failed to submit", response)

        return False

    def save_whole_database_to_json(self, outfile):
        response = self.table.scan()
        with open(outfile, 'w') as f:
            # Use the custom default function for JSON serialization
            json.dump(response, f, default=decimal_default, indent=4)

    def load_all_submissions(self, team):
        response = self.table.query(
            KeyConditionExpression=Key('team').eq(team)
        )
        return response['Items']

    def load_latest_submission(self, team):
        response = self.table.query(
            KeyConditionExpression=Key('team').eq(team),
            ScanIndexForward=False,
            Limit=1
        )
        return response['Items']

if __name__ == "__main__":
    with open('.credentials.json') as f:
        credentials = json.load(f)

    db = DBClient(credentials['AWS_ACCESS_KEY_ID'], credentials['AWS_ACCESS_KEY_SECRET'])
    exists = db.is_already_submitted('team1', 'hash1')

    if not exists:
            
        exists = db.submit({
            'yeam': 'team1',
            'commit_hash': 'hash1',
        })
        
        print(exists)