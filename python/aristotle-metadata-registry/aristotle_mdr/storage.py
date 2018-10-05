from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from urllib.parse import unquote, urldefrag, urlsplit, urlunsplit

import hashlib
import re


class CustomManifestStaticFilesStorage(ManifestStaticFilesStorage):

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
