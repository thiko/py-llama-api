import logging as log
import os

import boto3
import botocore


class S3Bucket:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client("s3")

    def upload_file(self, local_file_path: str, destination_objectname: str):
        try:
            self.s3.upload_file(
                local_file_path, self.bucket_name, destination_objectname
            )
            print("File uploaded successfully!")
        except Exception as e:
            print("Error uploading file: ", e)

    def download_file(self, object_key: str, local_file_path: str) -> bool:
        try:
            self.s3.download_file(
                self.bucket_name, object_key, local_file_path
            )
            print("File downloaded successfully!")
            return True
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("The object does not exist.")
                return False
            else:
                raise

    def download_s3_folder(self, s3_folder_name: str, local_folder_path: str):
        bucket = self.s3.Bucket(self.bucket_name)

        for obj in bucket.objects.filter(Prefix=s3_folder_name):
            target = os.path.join(
                local_folder_path, os.path.relpath(obj.key, s3_folder_name)
            )
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            try:
                bucket.download_file(obj.key, target)
                print("File downloaded successfully: ", target)
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    print("The object does not exist: ", obj.key)
                else:
                    raise

    def get_list_of_objects(self):
        # use the list_objects_v2 method to get a list of all objects in the bucket
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)

        # iterate over the 'Contents' key of the response dictionary to get a list of all files
        for obj in response["Contents"]:
            print(obj["Key"])

    def remove_file(self, object_key: str):
        try:
            self.bucket.Object(object_key).delete()
            log.info("File deleted successfully: %s" % object_key)
        except Exception as e:
            log.error("Error deleting file: ", e)
