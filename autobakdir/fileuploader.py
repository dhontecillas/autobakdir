import os
import sys
import boto3

def _aws_key_and_secret(aws_key_id, aws_secret):
    try:
        if aws_key_id is None:
            aws_key_id = os.environ['AWS_ACCESS_KEY_ID']
        if aws_secret is None:
            aws_secret = os.environ['AWS_SECRET_ACCESS_KEY']
        return aws_key_id, aws_secret
    except KeyError:
        # TODO: Log the error
        return None, None

def _aws_bucket(bucket_name):
    try:
        if bucket_name is None:
            bucket_name = os.environ['AWS_BUCKET_NAME']
        return bucket_name
    except KeyError:
        # TODO: Log the error
        return None

def aws_s3_client(aws_key_id, aws_secret):
    key_id, key_secret = _aws_key_and_secret(aws_key_id, aws_secret)
    if key_id is None or key_secret is None:
        return None
    client = boto3.client('s3', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_secret)
    return client

def aws_upload_file(fullpath_name,
                    s3_client,
                    bucket_name,
                    content_type=None):
    bucket_name = _aws_bucket(bucket_name)
    if not s3_client or not bucket_name:
        print( 'no client , no bucket {} {}'.format(s3_client, bucket_name))
        return False
    def percent_cb(complete):
        sys.stdout.write('  * {} * '.format(complete))
        sys.stdout.flush()
    try:
        # ContentType : image/jpeg
        if content_type:
            extra_args = {'ContentType' : content_type}
        else:
            extra_args = {}
        res = s3_client.upload_file(fullpath_name, bucket_name,
                                   os.path.basename(fullpath_name),
                                   ExtraArgs=extra_args,
                                   Callback=percent_cb)
        return True
    except Exception as ex:
        print('upload exception')
        print(ex)
        return False

def aws_check_exists(filename, s3_client, bucket_name=None):
    filename = os.path.basename(filename)
    bucket_name = _aws_bucket(bucket_name)
    if not bucket_name:
        return False
    try:
        res = s3_client.head_object(Bucket=bucket_name, Key=filename)
        if res:
            return True
    except Exception as ex:
        return False

def aws_download_file(filename, download_fpath, client_s3, bucket_name=None):
    bucket_name = _aws_bucket(bucket_name)
    if not bucket_name:
        return False
    download_file = os.path.join(download_fpath, filename)
    client_s3.download_file(bucket_name, filename, download_file)
    return True

def aws_upload_if_not_exists(fullpath_name, s3_client, bucket_name, content_type):
    base_name = os.path.basename(fullpath_name)
    if aws_check_exists(base_name, s3_client, bucket_name):
        return True # already exists
    return aws_upload_file(fullpath_name, s3_client, bucket_name)
