#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Red Hat, Inc. <http://www.redhat.com/>
# This file is part of GlusterFS.
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime

import changelogparser

history = []
file_gfids = set()
args = None
paths_to_trace = set()
turn = 0


def human_time(ts):
    return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S")


def get_args():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=__doc__)

    parser.add_argument("changelogs_list",
                        help="List of Changelogs to process")
    parser.add_argument("pgfid", help="Parent directory GFID")
    parser.add_argument("basename", help="Basename of File")
    parser.add_argument("--trace-rename", action="store_true",
                        help="Trace Renamed Files")
    return parser.parse_args()


def process_changelog_record(record):
    global args, history, file_gfids, paths_to_trace, turn

    # If Trace Rename is Set, Do not process in first turn, Collect
    # all possible path names in case of Rename.
    if turn == 0 and args.trace_rename and record.fop != "RENAME":
        return

    if record.fop in ["CREATE", "MKNOD"]:
        # If the File we are tracking is Created then add to history
        if record.path in paths_to_trace:
            history.append((record.ts, record.gfid,
                            "{0} {1}".format(record.fop,
                                             record.path)))
            file_gfids.add(record.gfid)
    elif record.fop_type == "D":
        # If the GFID we are tracking is modified then add to history
        if record.gfid in file_gfids:
            history.append((record.ts, record.gfid, "DATA"))
    elif record.fop_type == "M":
        # If the GFID we are tracking is modified then add to history
        if record.gfid in file_gfids:
            history.append((record.ts, record.gfid, "META"))
    elif record.fop == "RENAME" and args.trace_rename:
        # If New path is in the paths_to_trace list then start
        # tracking old name too
        if turn == 0 and args.trace_rename:
            if record.path2 in paths_to_trace:
                paths_to_trace.add(record.path1)

            return

        # Add to history if old name is in tracking list
        if record.path1 in paths_to_trace:
            paths_to_trace.add(record.path2)
            history.append((record.ts, record.gfid,
                            "{0} {1} {2}".format(
                                record.fop,
                                record.path1,
                                record.path2)))
    elif record.fop == "UNLINK":
        # If the file which we are tracking is unlinked
        pgfid, bn = record.path.split("/")
        if record.path in paths_to_trace:
            history.append((record.ts, record.gfid,
                            "{0} {1}".format(
                                record.fop,
                                record.path)))


def main():
    global args, history, paths_to_trace, turn

    args = get_args()
    paths_to_trace.add("{0}/{1}".format(args.pgfid, args.basename))

    with open(args.changelogs_list) as f:
        for line in f:
            changelogparser.parse(line.strip(),
                                  callback=process_changelog_record)

        if args.trace_rename:
            f.seek(0)
            turn += 1
            for line in f:
                changelogparser.parse(line.strip(),
                                      callback=process_changelog_record)

    if history:
        print("{0:20s}   {1:36s}   {2}".format("DATE", "GFID", "DETAILS"))
        print("-"*70)

    for line in history:
        print("{0:20s}   {1:36s}   {2}".format(human_time(line[0]),
                                               line[1], line[2]))


if __name__ == "__main__":
    main()
