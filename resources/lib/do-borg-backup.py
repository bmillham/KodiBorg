#!/usr/bin/python3

# An example of how the module could be used.

import os
from myborg.myborg import MyBorg
from myborg.helper import Helper

helper = Helper()

# Initialize the module. Also reads the xml config
borg = MyBorg(showcmd=True, config_file='/home/brian/.kodi/userdata/addon_data/plugin.script.MyBorg/settings.xml')

# This example will override the xml config for estimate type.
# Forces it to fast

if borg.estimatefiles != 'none':
    print(f'Estimating file count: {borg.estimatefiles}')
    e = borg.estimate()
    if type(e) is int:
        estimated = e
        helper.estimated = e
    elif e is None:
        print("No previous backup to get estimate from")
        estimated = 0
        helper.estimated = 0
    else:
        for est in e:
            if est['type'] == 'log_message':
                print(est['message'])
                continue
            if est['finished']:
                estimated = est['nfiles']
                helper.estimated = est['nfiles']
            else:
                print(f"Estimating file count: {est['nfiles']}", end="\r", flush=True)
    print(f"\nEstimated files to check: {estimated}")
else:
    print("Not estimating file count")
    estimated = 0

progress_status = {}

# Stuff to make the formatting pretty for command line. Could also
# be used from Kodi.

saved_lines = []

# Start the actual backup.
# You could do borg.showcmd = True to see the generated borg command line
# if you want. Can be helpful for debugging.

for i in borg.create():
    if i['type'] == 'progress_percent':
        if i['msgid'] not in progress_status:
            print()
            progress_status[i['msgid']] = i['finished']
        if i['finished']:
            print(f"Completed: {i['msgid']}")
        else:
            print(f"{i['message']}")
    elif i['type'] == 'log_message':
        print(f"{i['message']}")
        if i['msgid'] == "Repository.DoesNotExist":
            print("Please run do-borg-init.py to create the borg repository!")
            break
    elif i['type'] == 'progress_message':
        if i['msgid'] not in progress_status:
            progress_status[i['msgid']] = i['finished']
            if i['msgid'] == 'cache.begin_transaction':
                print(f"{i['message']}")
        else:
            if i['finished']:
                progress_status[i['msgid']] = True
                if i['msgid'] == 'cache.begin_transaction':
                    print(f"Cache initialized")
                    if not helper.headerprinted:
                        helper.header()
                        for l in saved_lines:
                            print(l, end="\r", flush=True)
            else:
                print(f"{i['message']}")

    elif i['type'] == 'backup_done':
        results = i['results']
        if results is None:
            print("Backup failed")
            continue

        print()
        summary = helper.format_summary(results)
        for l in summary:
            print(l)
    else:
        if i['type'] == 'return_code':
            if i['code'] != 0:
                print(f"The backup was aborted ({i['code']})")
                exit(i['code'])
            else:
                continue
        if estimated > 0 and i['nfiles'] > estimated:
            estimated = i['nfiles']
        if i['path'] == '':
            continue
        line = helper.format_status_line(i)
        if not helper.headerprinted:
            saved_lines.append(line)
        else:
            print(line, end="\r", flush=True)
