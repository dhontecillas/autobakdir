"""Autobakdir

Usage:
    autobackdir.py <root_dir> <control_file> <tmp_dir> <zip_name>
"""

import os

from docopt import docopt

from core import backup_if_required

if __name__ == '__main__':
#    control_file = '/home/dhontecillas/tmp/deleteme_control_file'
#    root_dir  = '/home/dhontecillas/tmp/deleteme_test_files'
#    tmp_zip_dir = '/home/dhontecillas/tmp'
    args = docopt(__doc__)
    root_dir = os.path.expanduser(args['<root_dir>'])
    control_file = os.path.expanduser(args['<control_file>'])
    tmp_dir = os.path.expanduser(args['<tmp_dir>'])
    zipname = os.path.expanduser(args['<zip_name>'])
    backup_if_required(root_dir, control_file, tmp_dir, zipname)
