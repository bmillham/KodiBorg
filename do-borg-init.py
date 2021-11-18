#!/usr/bin/python3

from myborg.myborg import MyBorg

borg = MyBorg(config_file='/home/brian/.kodi/userdata/addon_data/plugin.script.MyBorg/settings.xml')

# Create a new repo
# borg.showoutput=True
#borg.showcmd=True

error=0

for l in borg.init():
    if l['type'] == 'log_message':
        print(l['message'])
        #error += 1
    elif l['type'] == 'return_code':
        if l['code'] != 0:
            #print(f"Unable to create repo: {borg.repo_path} ({l['code']})")
            error = l['code']
            
    elif l['type'] == 'backup_done':
        if error == 0:
            print(f"{borg.repo_path} created")
        else:
            print(f"Unable to create repo: {borg.repo_path} ({error})")

