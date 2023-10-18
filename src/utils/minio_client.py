import logging
from datetime import timedelta

from minio import Minio as Base


class Minio(Base):
    def __init__(self, minio_url: str, access_key: str, secret_key: str, bucket_name: str):
        self.bucket_name = bucket_name
        super().__init__(
            minio_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

    def presigned_get_file(self, file_name) -> str:
        url = self.presigned_get_object(bucket_name=self.bucket_name, object_name=file_name, expires=timedelta(days=7))
        return url

    def check_file_exists(self, file_name) -> bool:
        try:
            self.stat_object(bucket_name=self.bucket_name, object_name=file_name)
            return True
        except Exception as e:
            logging.warning(e)
            return False

    def upload_file(self, file_data, file_name, content_type) -> str:
        object_name = file_name
        self.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=file_data,
            content_type=content_type,
            length=-1,
            part_size=10 * 1024 * 1024,
        )
        url = self.presigned_get_object(bucket_name=self.bucket_name, object_name=object_name)
        return url
