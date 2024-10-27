import os
import configparser
from scripts.reddit_etl import connect_reddit, extract_posts, transform_data, load_data_to_csv


parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.conf'))

REDDIT_SECRET_KEY = parser.get('api_keys', 'REDDIT_SECRET_KEY')
REDDIT_CLIENT_ID = parser.get('api_keys', 'REDDIT_CLIENT_ID')
OUTPUT_PATH = parser.get('file_paths', 'OUTPUT_PATH')

def reddit_pipeline(file_name: str, subreddit: str, limit=None):
    
    instance = connect_reddit(REDDIT_CLIENT_ID, REDDIT_SECRET_KEY, 'AGENT')
    
    posts, comments = extract_posts(instance, subreddit, limit)
    
    df = transform_data(posts, comments)
   
    file_path = f'{OUTPUT_PATH}/{file_name}.csv'
    load_data_to_csv(df, file_path)

    return file_path