#!/usr/bin/python3

# An example of how the module could be used.

import os
from kodiborg.run import Run

# This is just so it looks nice running from the command line.
# If called from Kodi then something like this probably would not be needed.

def header(flen, fsize, ncsize, psize):
    print()
    print(f"{'Current':{flen}}   {'Total':{fsize}} | {'File':>{ncsize}} |")
    print(f"{'File':{flen}} | {'Size':{fsize}} | {'Count':>{ncsize}} | {'Progress':^{psize}}")

# Initialize the module. Also reads the xml config
borg = Run()

# This example will override the xml config for estimate type.
# Forces it to fast

borg.estimatefiles = 'fast'
if borg.estimatefiles != 'none':
    print(f'Estimating file count: {borg.estimatefiles}')
    e = borg.estimate()
    if type(e) is int:
        estimated = e
    else:
        for est in e:
            if est['type'] == 'log_message':
                print(est['message'])
                continue
            if est['finished']:
                estimated = est['nfiles']
            else:
                print(f"Estimating file count: {est['nfiles']}", end="\r", flush=True)
    print(f"\nEstimated files to check: {estimated}")
else:
    print("Not estimating file count")
    estimated = 0

progress_status = {}

# Stuff to make the formatting pretty for command line. Could also
# be used from Kodi.

flen="<40.40"
fsize=">9.9"
psize="8.8"
ncsize="6"
header_printed=False
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
        print(f"Unexpected log message: {i['message']}")
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
                    if not header_printed:
                        header(flen, fsize, ncsize, psize)
                        header_printed = True
                        for l in saved_lines:
                            print(l, end="\r", flush=True)
            else:
                print(f"{i['message']}")

    elif i['type'] == 'backup_done':
        results = i['results']
        if results is None:
            print("Backup failed")
            continue
        archive = results['archive']
        cache = results['cache']
        print(f"\nArchive name: {archive['name']}")
        print(f"Archive fingerprint: {archive['id']}")
        print(f"Time (start): {archive['start']}")
        print(f"Time (end):   {archive['end']}")
        print(f"Duration: {archive['duration']} seconds")
        print(f"Number of files: {archive['stats']['nfiles']}")
        print(f"Utilization of max. archive size: {archive['limits']['max_archive_size']:.0f}%")
        print()
        a_stats = archive['stats']
        c_stats = cache['stats']
        print(f"{'':13.13} "
              f"{'Original Size':13.13} "
              f"{'Compressed Size':15.15} "
              f"{'Deduplicated Size':17.17}")
        print(f"{'This archive:':13.13} "
              f"{borg.format_bytes(a_stats['original_size']):>13.13} "
              f"{borg.format_bytes(a_stats['compressed_size']):>15.15} "
              f"{borg.format_bytes(a_stats['deduplicated_size']):>17.17}")
        print(f"{'All archives:':13.13} "
              f"{borg.format_bytes(c_stats['total_size']):>13.13} "
              f"{borg.format_bytes(c_stats['total_csize']):>15.15} "
              f"{borg.format_bytes(c_stats['unique_size']):>17.17}")
        print()
        print(f"{'':13.13} "
              f"{'Unique chunks':13.13} "
              f"{'Total chunks':>15.15}")
        print(f"{'Chunk index:':13.13} "
              f"{c_stats['total_unique_chunks']:>13d} "
              f"{c_stats['total_chunks']:>15d}")
    else:
        if i['nfiles'] > estimated:
            estimated = i['nfiles']
        if i['path'] == '':
            continue
        line = (f"{os.path.split(i['path'])[1]:{flen}} | "
              f"{borg.format_bytes(i['original_size']):{fsize}} | "
              f"{i['nfiles']:{ncsize}d} | ")
        if borg.estimatefiles != 'none':
            line += f"{i['nfiles'] / estimated:0.1%}"
        else:
            line += "UNKNOWN"
        if not header_printed:
            saved_lines.append(line)
        else:
            print(line, end="\r", flush=True)

# You don't need to prune, or it could be a separate script.

if borg.prune_keep is None:
    print("\nWill not prune")
else:
    print("\nPruning the repo")
    for pline in borg.prune():
        if pline['type'] == 'prune_message':
            print(f"{pline['stat']}: {pline['name']}")
        elif pline['type'] == 'log_message': # Final stats from prune
            print(pline['message'])

