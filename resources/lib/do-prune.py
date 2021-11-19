#!/usr/bin/python3

# An example of how the module could be used to prune.

import os
from myborg.myborg import MyBorg

# This is just so it looks nice running from the command line.
# If called from Kodi then something like this probably would not be needed.

# Initialize the module. Also reads the xml config
borg = MyBorg(config_file='/home/brian/.kodi/userdata/addon_data/plugin.script.MyBorg/settings.xml')

if borg.prune_keep is None:
    print("No prune configuration found. Doing nothing.")
else:
    print(f"Pruning the repository at {borg.repo_path}")
    print("Prune parameters")
    for p in borg.config.prune_details:
        print(f"{p:>12}: {borg.config.prune_details[p]:>2}")
    for pline in borg.prune():
        if pline['type'] == 'prune_message':
            print(f"{pline['stat']}: {pline['name']}")
        elif pline['type'] == 'log_message': # Final stats from prune
            print(pline['message'])

