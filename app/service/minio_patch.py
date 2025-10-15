from datetime import timedelta, datetime
from typing import Optional
from urllib.parse import urlunsplit

from minio import time
from minio.helpers import DictType, check_bucket_name, check_object_name, BaseURL
from minio.signer import presign_v4


def presigned_get_object(
        self,
        base_host: str,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(days=7),
        response_headers: Optional[DictType] = None,
        request_date: Optional[datetime] = None,
        version_id: Optional[str] = None,
        extra_query_params: Optional[DictType] = None,
) -> str:
    """
    Get presigned URL of an object to download its data with expiry time
    and custom request parameters.

    :param base_host: Base host URL.
    :param bucket_name: Name of the bucket.
    :param object_name: Object name in the bucket.
    :param expires: Expiry in seconds; defaults to 7 days.
    :param response_headers: Optional response_headers argument to
                              specify response fields like date, size,
                              type of file, data about server, etc.
    :param request_date: Optional request_date argument to
                          specify a different request date. Default is
                          current date.
    :param version_id: Version ID of the object.
    :param extra_query_params: Extra query parameters for advanced usage.
    :return: URL string.

    Example::
        # Get presigned URL string to download 'my-object' in
        # 'my-bucket' with default expiry (i.e. 7 days).
        url = client.presigned_get_object("my-bucket", "my-object")
        print(url)

        # Get presigned URL string to download 'my-object' in
        # 'my-bucket' with two hours expiry.
        url = client.presigned_get_object(
            "my-bucket", "my-object", expires=timedelta(hours=2),
        )
        print(url)e2
    """
    method = 'GET'
    region = self._get_region(bucket_name)
    base_url = BaseURL(
        base_host,
        region,
    )
    check_bucket_name(bucket_name, s3_check=base_url.is_aws_host)
    check_object_name(object_name)
    if expires.total_seconds() < 1 or expires.total_seconds() > 604800:
        raise ValueError("expires must be between 1 second to 7 days")

    region = self._get_region(bucket_name)
    query_params = extra_query_params or {}
    query_params.update({"versionId": version_id} if version_id else {})
    query_params.update(response_headers or {})
    creds = self._provider.retrieve() if self._provider else None
    if creds and creds.session_token:
        query_params["X-Amz-Security-Token"] = creds.session_token
    url = base_url.build(
        method=method,
        region=region,
        bucket_name=bucket_name,
        object_name=object_name,
        query_params=query_params,
    )

    if creds:
        url = presign_v4(
            method=method,
            url=url,
            region=region,
            credentials=creds,
            date=request_date or time.utcnow(),
            expires=int(expires.total_seconds()),
        )
    return urlunsplit(url)
