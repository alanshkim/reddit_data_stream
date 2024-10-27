import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add path for pipeline modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines.reddit_pipeline import reddit_pipeline
from scripts.load_to_aws import load_to_s3

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["alanshkim@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

file_datefix = datetime.now().strftime("%Y%m%d")

with DAG(
    dag_id="reddit_etl_dag",
    default_args=default_args,
    schedule_interval=timedelta(days=1), # '@daily'
    start_date=datetime(2024, 10, 26),
    catchup=False,
    tags=['reddit', 'etl', 'pipeline']
) as dag:

    reddit_etl_task = PythonOperator(
        task_id="reddit_etl_task",
        python_callable=reddit_pipeline,
        op_kwargs={
            "file_name": f"reddit_{file_datefix}",
            "subreddit": "dataengineering", 
            "limit": 100
            },
    )

    load_to_aws_s3 = PythonOperator(
        task_id='aws_s3_upload',
        python_callable=load_to_s3
    )

    reddit_etl_task >> load_to_aws_s3