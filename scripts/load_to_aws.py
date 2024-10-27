import os
import s3fs
import configparser

parser = configparser.ConfigParser()
parser.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.conf'))

bucket = parser.get('aws_s3', 'AWS_BUCKET_NAME')

def load_to_s3(ti):

    file_path = ti.xcom_pull(task_ids='reddit_etl_task', key='return_value')
    file_name = file_path.split('/')[-1]

    s3 = s3fs.S3FileSystem(anon=False)

    try:
        if not s3.exists(bucket):
            s3.mkdir(bucket)
            print("Bucket created")
        else :
            print("Bucket already exists")
    except Exception as e:
        print(e)
    try:
        s3.put(file_path, bucket+'/raw/'+ file_name)
        print('File uploaded to s3')
    except FileNotFoundError:
        print('File does not exist')