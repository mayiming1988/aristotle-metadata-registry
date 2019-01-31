from aristotle_mdr.utils import fetch_aristotle_downloaders


def get_download_class(download_type: str):
    downloader_class = None
    dl_classes = fetch_aristotle_downloaders()
    for klass in dl_classes:
        if klass.download_type == download_type:
            downloader_class = klass
    return downloader_class
