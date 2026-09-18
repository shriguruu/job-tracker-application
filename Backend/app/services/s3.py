import os
from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from app.core.config import settings
from app.core.exceptions import AppException


class S3Service:
    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_REGION
        self.endpoint_url = settings.AWS_ENDPOINT_URL
        self.mock_mode = os.getenv("USE_LOCAL_S3_MOCK", "false").lower() in ("true", "1", "yes")

        client_kwargs = {"region_name": self.region}
        if self.endpoint_url:
            client_kwargs["endpoint_url"] = self.endpoint_url

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        # Boto3 client uses IAM role automatically if access keys are omitted
        self._s3_client = None
        self._client_kwargs = client_kwargs

        if self.mock_mode:
            self._local_storage_dir = os.path.join(os.getcwd(), ".local_s3_storage")
            os.makedirs(self._local_storage_dir, exist_ok=True)

    @property
    def client(self):
        if self._s3_client is None and not self.mock_mode:
            try:
                self._s3_client = boto3.client("s3", **self._client_kwargs)
            except Exception as e:
                # Fallback to mock mode if credentials/AWS unavailable during local dev/tests
                self.mock_mode = True
                self._local_storage_dir = os.path.join(os.getcwd(), ".local_s3_storage")
                os.makedirs(self._local_storage_dir, exist_ok=True)
        return self._s3_client

    def upload_file(self, file_obj: BinaryIO, object_key: str, content_type: str = "application/pdf") -> None:
        """Upload a file stream to S3 or local mock."""
        if self.mock_mode or self.client is None:
            dest_path = os.path.join(self._local_storage_dir, object_key.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(file_obj.read())
            return

        try:
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )
        except (ClientError, BotoCoreError) as e:
            raise AppException(
                status_code=500,
                code="S3_UPLOAD_FAILED",
                message=f"Failed to upload file to storage: {str(e)}",
            )

    def generate_presigned_url(self, object_key: str, expires_in: int = 300) -> str:
        """Generate a pre-signed GET URL for downloading the file."""
        if self.mock_mode or self.client is None:
            # Return local static or mock URL
            return f"/api/v1/resumes/mock-download/{object_key}"

        try:
            url = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_key,
                    "ResponseContentDisposition": "attachment",
                },
                ExpiresIn=expires_in,
            )
            return url
        except (ClientError, BotoCoreError) as e:
            raise AppException(
                status_code=500,
                code="S3_PRESIGN_FAILED",
                message=f"Failed to generate pre-signed URL: {str(e)}",
            )

    def delete_file(self, object_key: str) -> None:
        """Delete a file from S3 or local mock."""
        if self.mock_mode or self.client is None:
            dest_path = os.path.join(self._local_storage_dir, object_key.replace("/", os.sep))
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            return

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
        except (ClientError, BotoCoreError):
            pass


s3_service = S3Service()
