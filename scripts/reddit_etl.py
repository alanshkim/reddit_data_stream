import os
import sys
import yaml
import pandas as pd
import praw
from praw import Reddit

fields_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'post_fields.yml')

with open(fields_path, 'r') as file:
    data = yaml.safe_load(file)

POST_FIELDS = data['POST_FIELDS']

def connect_reddit(client_id, client_secret, user_agent) -> Reddit:
    try:
        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent)
        print("Connected to Reddit!")
        return reddit
    except Exception as e:
        print(e)
        sys.exit(1)

def extract_posts(reddit_instance: Reddit, subreddit: str, limit=None):

    subreddit = reddit_instance.subreddit(subreddit)
    posts = subreddit.hot(limit=limit)

    posts_list = []
    comments_list = []
    
    for post in posts:
        post_dict = vars(post)
        post_data = {field: post_dict[field] for field in POST_FIELDS}
        posts_list.append(post_data)

        post.comments.replace_more(limit=None)
        for comment in post.comments.list():
            comment_data = {
            "post_id": post.id,
            "comment_id": comment.id,
            "author": str(comment.author),
            "body": comment.body,
            "score": comment.score,
            "created_utc": comment.created_utc,
            "parent_id": comment.parent_id
        }
            comments_list.append(comment_data)
        
        return posts_list, comments_list

def transform_data(posts: list, comments: list):

    posts_df = pd.DataFrame(posts)
    comments_df = pd.DataFrame(comments)

    df = posts_df.merge(comments_df, right_on=['post_id'], left_on=['id'], how='left', suffixes=('_post', '_cmnt'))

    df['created_utc_post'] = pd.to_datetime(df['created_utc_post'], unit='s')
    df['created_utc_cmnt'] = pd.to_datetime(df['created_utc_cmnt'], unit='s')
    df['author_post'] = df['author_post'].astype(str)
    df['author_cmnt'] = df['author_cmnt'].astype(str)
    df['num_comments'] = df['num_comments'].astype(int)
    df['score_post'] = df['score_post'].astype(int)
    df['score_cmnt'] = pd.to_numeric(df['score_cmnt'], errors='coerce')
    df['title'] = df['title'].astype(str)

    return df

def load_data_to_csv(data: pd.DataFrame, path: str):
    data.to_csv(path, index=False)