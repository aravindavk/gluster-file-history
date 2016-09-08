# Find History of a File

A Changelog based tool to track a file's life cycle in a Gluster Volume.

## Prerequisites
Changelog should be enabled before any I/O. This tool only parses
Changelogs to find History of a file.

## Usage

Collect the list of changelog file paths for required time range

Example: cat /tmp/changelogs.txt

    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473252656
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473252671
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473252686
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473252821
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473253871
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473253886
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473255491
    /bricks/b1/.glusterfs/changelogs/CHANGELOG.1473255506

Run `main.py` with required arguments to trace the File

    usage: main.py [-h] [--trace-rename] changelogs_list pgfid basename
     
    positional arguments:
      changelogs_list  List of Changelogs to process
      pgfid            Parent directory GFID
      basename         Basename of File
     
    optional arguments:
      -h, --help       show this help message and exit
      --trace-rename   Trace Renamed Files

Example:

    python main.py /tmp/changelogs.txt 00000000-0000-0000-0000-000000000001 f1

Example output,

    DATE                   GFID                                   DETAILS
    ----------------------------------------------------------------------
    2016-09-07 18:21:11    7555aff2-5a9e-496a-a646-98731992af1a   CREATE 00000000-0000-0000-0000-000000000001/f1
    2016-09-07 18:21:11    7555aff2-5a9e-496a-a646-98731992af1a   DATA
    2016-09-07 18:21:26    7555aff2-5a9e-496a-a646-98731992af1a   DATA


To get Parent GFID, Run `getfattr` on directory in Mount,

    getfattr -n glusterfs.gfid.string <PATH_TO_DIR>

Example:

    getfattr -n glusterfs.gfid.string /mnt/gv1/d1

## Special Case: Rename
If a file is renamed to different name and unlinked or if we have only
the latest name then use `--trace-rename` option.

For example, if "f1" is renamed to "f2" and then unlinked, Above
script will print 

    DATE                   GFID                                   DETAILS
    ----------------------------------------------------------------------
    2016-09-07 18:21:11    7555aff2-5a9e-496a-a646-98731992af1a   CREATE 00000000-0000-0000-0000-000000000001/f1
    2016-09-07 18:21:11    7555aff2-5a9e-496a-a646-98731992af1a   DATA
    2016-09-07 18:21:26    7555aff2-5a9e-496a-a646-98731992af1a   DATA
    2016-09-07 18:23:41    7555aff2-5a9e-496a-a646-98731992af1a   RENAME 00000000-0000-0000-0000-000000000001/f1 00000000-0000-0000-0000-000000000001/f2
    2016-09-07 18:41:11    7555aff2-5a9e-496a-a646-98731992af1a   UNLINK 00000000-0000-0000-0000-000000000001/f2

## Known issues
- Date shown in output is Changelog Rollover time, Actual FOP may
  happened before that time(Upto 15 secs)
- Data operations may get missed if a file is renamed and hashed to
  different brick.
- Rename after Rebalance may record the future events in different
  brick.
