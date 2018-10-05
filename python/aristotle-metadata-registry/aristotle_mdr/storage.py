from django.contrib.staticfiles.storage import ManifestFilesMixin, StaticFilesStorage
from django.conf import settings
from urllib.parse import unquote, urldefrag, urlsplit, urlunsplit

import hashlib
import re
import os
import json


class LocalManifestMixin:

    def __init__(self, *args, **kwargs):
        self.manifest_location = os.path.abspath(os.path.join(settings.BASE_DIR, self.manifest_name))
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
        regex = re.compile('.*[0-9a-f]{16}.bundle.(js|css)$')

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


class CustomManifestStaticFilesStorage(LocalManifestMixin,
                                       SelectiveHashingMixin,
                                       ManifestFilesMixin,
                                       StaticFilesStorage):
    pass
