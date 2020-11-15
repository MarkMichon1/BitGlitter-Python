import json
import logging
import os
import pathlib


def package_files(file_list, working_directory, mask_enabled):

    logging.info('Packaging files...')


    manifest = {'somefolder' : {'file': 'ok'}, 'testing': 123}

    for path_string in file_list:
        #Crawl.... glob?

        # filesize, hash
        if mask_enabled:
            pass

    manifest = json.dumps(manifest)
    return manifest