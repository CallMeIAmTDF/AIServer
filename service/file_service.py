import mimetypes
import time

from const.rag import STORE_NAME


def upload_file(
    client,
    file_path: str,
    display_name: str,
):
    if not STORE_NAME:
        raise RuntimeError("FILE_SEARCH_STORE_NAME is not configured")

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=STORE_NAME,
        config={
            "display_name": display_name,
            "mime_type": mime_type,
        },
    )

    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)

    return operation.response