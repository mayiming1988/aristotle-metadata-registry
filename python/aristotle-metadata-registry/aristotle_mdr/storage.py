from django.contrib.staticfiles.storage import ManifestFilesMixin
from django.conf import settings
from urllib.parse import unquote, urlsplit
import hashlib
import re
import os
import json

from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile


class LocalManifestMixin:
    """
    Stores the manifest.json file on the local filesystem
    Currently not being used
    """

    def __init__(self, *args, **kwargs):
        self.manifest_location = os.path.join(settings.MANIFEST_DIR, self.manifest_name)
        super().__init__(*args, **kwargs)

    # Locally stored manifest
    def read_manifest(self):
        try:
            with open(self.manifest_location) as manifest:
                return manifest.read()
        except IOError:
            return None

    def save_manifest(self):
        print('Saving to {}'.format(self.manifest_location))
        payload = {'paths': self.hashed_files, 'version': self.manifest_version}

        if os.path.isfile(self.manifest_location):
            os.remove(self.manifest_location)

        contents = json.dumps(payload)

        try:
            with open(self.manifest_location, 'w') as manifest:
                manifest.write(contents)
        except IOError:
            print('Error writing manifest file')


class SelectiveHashingMixin:
    """
    Allows hashing to be skipped for certain files
    Not currently used
    """

    # If a file matches this pattern it will not be hashed by django
    ignore_pattern: str = r'.*[0-9a-f]{16}.bundle.(js|css)$'

    # Use a 16 length sha256 hash
    def file_hash(self, name, content=None):
        """
        Return a hash of the file with the given name and optional content.
        """
        if content is None:
            return None
        sha = hashlib.sha256()
        for chunk in content.chunks():
            sha.update(chunk)
        return sha.hexdigest()[:16]

    def hashed_name(self, name, content=None, filename=None):
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path.strip()
        regex = re.compile(self.ignore_pattern)

        if content is not None:
            # Check if the filename has already been hashed
            file_hash = self.file_hash(clean_name, content)
            if file_hash in name:
                # Check if the hash is in the name (will work for file-loader
                # images)
                print('Already Hashed: {}'.format(name))
                return name
            elif regex.fullmatch(name) is not None:
                # Check if passes regex
                print('Already Hashed: {}'.format(name))
                return name

        return super().hashed_name(name, content, filename)


# Fixes I/O error on computing hash thanks to
# https://github.com/jschneier/django-storages/issues/382#issuecomment-377174808
class CustomS3Boto3Storage(S3Boto3Storage):

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(CustomS3Boto3Storage, self)._save_content(obj, content_autoclose, parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()


class CustomManifestStaticFilesStorage(ManifestFilesMixin,
                                       CustomS3Boto3Storage):

    max_post_process_passes = 1
    patterns = ()
