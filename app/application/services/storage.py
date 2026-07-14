import logging
from botocore.exceptions import ClientError
from app.infrastructure.aws import get_s3_client

logger = logging.getLogger(__name__)

class StorageService:
    """Application Service for managing S3 cloud storage operations via Boto3."""
    # Communicates with S3 (LocalStack in development) using endpoint configurations.
    def __init__(self, bucket_name: str = 'electrostock-bucket') -> None:
        self.bucket_name = bucket_name
        self.s3_client = get_s3_client()

    def create_bucket(self, bucket_name: str | None = None) -> bool:
        """Creates the bucket if it does not already exist."""
        target_bucket = bucket_name or self.bucket_name
        try:
            try:
                self.s3_client.head_bucket(Bucket=target_bucket)
                logger.info(f"S3 bucket '{target_bucket}' already exists.")
                return True
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code in ['404', 'NoSuchBucket']:
                    logger.info(f"S3 bucket '{target_bucket}' not found. Creating bucket...")
                    region_name = self.s3_client.meta.region_name
                    if region_name == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=target_bucket)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=target_bucket,
                            CreateBucketConfiguration={'LocationConstraint': region_name}
                        )
                    logger.info(f"S3 bucket '{target_bucket}' created successfully.")
                    return True
                else:
                    logger.error(f"Error checking S3 bucket '{target_bucket}': {e}")
                    return False
        except Exception as e:
            logger.error(f"Failed to create S3 bucket '{target_bucket}': {e}")
            return False

    def upload_file(self, file_data, object_key: str) -> bool:
        """Uploads a file-like object to the configured S3 bucket and saves a local backup."""
        try:
            # 1. Save local backup copy for persistence
            import os
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            local_path = os.path.join(uploads_dir, object_key)
            
            # Seek to start
            file_data.seek(0)
            with open(local_path, 'wb') as f:
                f.write(file_data.read())
            
            # Seek back to start for S3 upload
            file_data.seek(0)

            # 2. Upload to S3
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                object_key
            )
            logger.info(f"Uploaded file '{object_key}' to S3 bucket '{self.bucket_name}' and saved local backup.")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file '{object_key}' to S3: {e}")
            return False

    def delete_file(self, object_key: str) -> bool:
        """Deletes an object from the S3 bucket and deletes its local backup."""
        try:
            # 1. Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            
            # 2. Delete from local backup
            import os
            uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'uploads')
            local_path = os.path.join(uploads_dir, object_key)
            if os.path.exists(local_path):
                os.remove(local_path)
                
            logger.info(f"Deleted file '{object_key}' from S3 bucket '{self.bucket_name}' and local backup.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file '{object_key}' from S3: {e}")
            return False

    def get_object_url(self, object_key: str) -> str:
        """Generates a readable URL for an S3 object."""
        # Automatically rewrites internal Docker hostnames to 'localhost' or the client-facing IP for browser access.
        if not object_key:
            return ""
        try:
            # Generate a presigned URL
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=3600
            )
            # Rewrite hostname if inside Docker network to allow host/client browser access
            target_host = "localhost"
            try:
                from flask import request
                if request:
                    target_host = request.host.split(':')[0]
            except RuntimeError:
                pass

            if "localstack:4566" in url:
                url = url.replace("localstack:4566", f"{target_host}:4566")
            elif "localhost:4566" in url:
                url = url.replace("localhost:4566", f"{target_host}:4566")
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL for '{object_key}': {e}")
            # Fallback simple URL structure
            endpoint_url = self.s3_client.meta.endpoint_url
            target_host = "localhost"
            try:
                from flask import request
                if request:
                    target_host = request.host.split(':')[0]
            except RuntimeError:
                pass

            if "localstack:4566" in endpoint_url:
                endpoint_url = endpoint_url.replace("localstack:4566", f"{target_host}:4566")
            elif "localhost:4566" in endpoint_url:
                endpoint_url = endpoint_url.replace("localhost:4566", f"{target_host}:4566")
            return f"{endpoint_url}/{self.bucket_name}/{object_key}"
