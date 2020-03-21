from datetime import timedelta
import os
from urllib.parse import urlparse

from google.cloud import storage

# Ref: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/storage/cloud-client/snippets.py


class GCS:

    def __init__(self):
        self.client = storage.Client('nogi-backup')

    @staticmethod
    def blob_name(typing: str, **kwargs) -> str:
        url = kwargs.get('url')
        video_name = kwargs.get('video_name')
        if not (url or video_name):
            raise ValueError('No key value input: %s' % kwargs)

        if url and typing == 'post':
            return urlparse(url).path[1:]
        if video_name and typing == 'video':
            return
        return ''

    def upload_stream(self, bucket: str, blob_name: str, content: str, content_type: str = 'text/plain') -> None:
        bucket = self.client.get_bucket(bucket)
        bucket.blob(blob_name).upload_from_string(data=content, content_type=content_type)

    def upload_file(self, bucket: str, blob_name: str, filepath: str, content_type: str = 'video/mp4') -> None:
        bucket = self.client.get_bucket(bucket)
        if os.path.isfile(filepath):
            bucket.blob(blob_name).upload_from_filename(filepath, content_type=content_type)
        else:
            raise FileNotFoundError(filepath)

    def list_objects(self, bucket: str, prefix: str, delimiter=None) -> list:
        bucket = self.client.get_bucket(bucket)
        blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        return [prefix for prefix in blobs.prefixes] if delimiter else blobs

    def generate_download_signed_url_v4(self, bucket: str, blob_name: str, expiration: int = 15) -> str:
        '''Generates a v4 signed URL for downloading a blob.
        Note that this method requires a service account key file. You can not use
        this if you are using Application Default Credentials from Google Compute
        Engine or from the Google Cloud SDK.
        '''
        bucket = self.client.get_bucket(bucket)
        return bucket.blob(blob_name).generate_signed_url(version='v4', expiration=timedelta(minutes=expiration), method='GET')
