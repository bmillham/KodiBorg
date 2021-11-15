#!/usr/bin/python3

# An example of how to get stats from a borg repo.

from myborg.myborg import MyBorg

info = MyBorg()
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
        print(f" Original size: {info.format_bytes(stats['original_size'])} "
              f"Compressed size: {info.format_bytes(stats['compressed_size'])} "
              f"Deduplicated size: {info.format_bytes(stats['deduplicated_size'])}")
