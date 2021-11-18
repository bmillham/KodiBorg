#!/usr/bin/python3

# An example of how to get stats from a borg repo.

from myborg.myborg import MyBorg
from myborg.helper import Helper

helper = Helper()
#info = MyBorg(config_file='borg-backup.xml')
info = MyBorg(config_file='/home/brian/.kodi/userdata/addon_data/plugin.script.MyBorg/settings.xml')
# Get info on the last nlast backups
nlast = 10

for i in info.info(archive_count=nlast):
    if i['type'] == 'return_code':
        print(f"borg info returned {i['code']}")
        break
    if i['results'] is None:
        print("Nothing returned from borg info. Probably an empty repo")
        break
    repo = i['results']['repository']
    print("Repository Information")
    print(f"    Location: {repo['location']}")
    print(f"    ID: {repo['id']}")
    print(f"    Modified: {repo['last_modified']}")
    print()
    print(f"Stats for the last {nlast} backups")
    for a in i['results']['archives']:
        stats = a['stats']
        print(f"Name: {a['name']} "
              f"Duration: {a['duration']} "
              f"Files: {stats['nfiles']}")
        print(f" Original size: {helper.format_bytes(stats['original_size'])} "
              f"Compressed size: {helper.format_bytes(stats['compressed_size'])} "
              f"Deduplicated size: {helper.format_bytes(stats['deduplicated_size'])}")
