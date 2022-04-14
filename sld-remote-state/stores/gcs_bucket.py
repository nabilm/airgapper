import json
import logging
from configs.gcs_bucket import settings

from google.cloud import storage


class GCStore(object):
    def __init__(self, path):
        self.path = path
        self.storage_client = storage.Client.from_service_account_json(settings.SERVICE_ACCOUNT_JSON)

    def get(self, id, bucket_name=settings.BUCKET):
        try:
            logging.info(f"Get remote state file {id}")
            bucket = self.storage_client.get_bucket(bucket_name)
            # get bucket data as blob
            tfstate_object = f'{id}.tfstate'
            if bucket.get_blob(tfstate_object):
                blob = bucket.get_blob(tfstate_object).download_as_string().decode("utf-8")
                return json.loads(blob)
            return False
        except Exception as err:
            logging.error(err)
            raise err

    def put(self, id, info, bucket_name=settings.BUCKET):
        try:
            logging.info(f"Put remote state file {id}")
            bucket = self.storage_client.get_bucket(bucket_name)

            blob = bucket.blob(f'{id}.tfstate')
            blob.upload_from_string(
                data = json.dumps(info),
                content_type='application/json'
            )
        except Exception as err:
            logging.error(err)
            raise err

    def lock(self, id, info, bucket_name=settings.BUCKET):
        try:
            logging.info(f"Lock remote state file {id}")
            lock_object = f'{id}.lock'
            # Set object as object GCS bucket
            bucket = self.storage_client.get_bucket(bucket_name)
            # Check if object exists
            if bucket.get_blob(lock_object):
                gcs_data = bucket.get_blob(lock_object).download_as_string().decode("utf-8")
                return False, json.loads(gcs_data)
            else:
                data = json.dumps(info, indent=4, sort_keys=True)
                bucket.blob(lock_object).upload_from_string(
                    data = json.dumps(info),
                    content_type='application/json'
                )
                return True, {id}
        except Exception as err:
            logging.error(err)
            return False

    def unlock(self, id, info, bucket_name=settings.BUCKET):
        try:
            logging.info(f"Unlock remote state file {id}")
            lock_object = f'{id}.lock'
            # Set object as object GCS bucket
            bucket = self.storage_client.get_bucket(bucket_name)
            # Delete object if exists
            if bucket.get_blob(lock_object):
                bucket.delete_blob(lock_object)
                return True
            return False
        except Exception as err:
            logging.error(err)
            return False

