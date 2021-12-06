import os
from typing import Generator

import boto3


class S3:

    def __init__(self, bucket_name: str, region: str = 'ap-northeast-1') -> None:
        self._bucket_name = bucket_name
        self.s3 = boto3.client('s3', region=region)

    def list_objects(self, prefix: str) -> Generator[None, str, None]:
        result = self.s3.list_objects(bucket=self._bucket_name, prefix=prefix)
        if result.get('Contents') is None:
            return None

        for obj in result['Contents']:
            yield obj['Key']

    def upload_object(self, prefix: str, object_name: str, object_content: bytes = None, object_path: str = '') -> None:
        if object_content:
            self.s3.upload_fileobj(
                Body=object_content,
                Bucket=self._bucket_name,
                Key=os.path.join(prefix, object_name)
            )
        if object_path:
            self.s3.meta.client.upload_file(
                Filename=object_path,
                Bucket=self._bucket_name,
                Key=os.path.join(prefix, object_name),
            )
        raise Exception('object_path and object_content are empty.')
