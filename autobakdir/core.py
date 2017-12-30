import os

from collections import namedtuple
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile

from fileuploader import aws_upload_file, aws_s3_client

FileInfo = namedtuple('FileInfo', ['fpath', 'mtime'])



def find_files(root_dir):
    if not root_dir.is_dir():
        raise ValueError('{} not a directory'.format(dirname))
    all_dirs = [root_dir]
    files = []
    while len(all_dirs):
        cur_dir = all_dirs.pop()
        for child in cur_dir.iterdir():
            if child.is_file():
                files.append(child.relative_to(root_dir))
            elif child.is_dir():
                all_dirs.append(child)
    files.sort()
    return files


def calc_hash(root_dir, filelist):
    hash_obj = sha256()
    for fpath in filelist:
        hash_obj.update(fpath.as_posix().encode('utf-8'))
        hash_obj.update(str((root_dir / fpath).stat().st_mtime).encode('utf-8'))
    return hash_obj.hexdigest()


def create_backup(root_dir, filelist, tmp_dir, zipname):
    """
    aws_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret = os.environ['AWS_SECRET_ACCESS_KEY']
    bucket_name = os.environ['AWS_BUCKET_NAME']
    """
    zfpath = (Path(tmp_dir) / Path(zipname)).as_posix()
    zfile = ZipFile(zfpath, 'w')
    for fpath in filelist:
        zfile.write((root_dir / fpath).as_posix(), fpath.as_posix())
    zfile.close()
    # upload backup,
    s3_client =  aws_s3_client(aws_key_id=None, aws_secret=None)
    res = aws_upload_file(zfpath, s3_client, bucket_name=None,
                          content_type='application/zip')
    print('result')
    print(res)
    print('- result')
    # unlink tmp file
    os.unlink(zfpath)


def backup_if_required(root_dir, control_file, tmp_dir, zipname):
    root_dir = Path(root_dir)
    last_hash = None
    try:
        with open(control_file, 'r') as hash_fp:
            last_hash = hash_fp.readline().strip()
            print('Last hash: {}'.format(last_hash))
    except FileNotFoundError:
        print('No control file found')

    files = find_files(root_dir)
    cur_hash = calc_hash(root_dir, files)
    print('Cur hash: {}'.format(cur_hash))
    if cur_hash == last_hash:
        print('No changes detected.. -> No backup')
    else:
        print('Dir files changed.. -> Creating backup')
        create_backup(root_dir, files, tmp_dir, zipname)
        try:
            with open(control_file, 'w') as hash_fp:
                hash_fp.write(cur_hash)
        except Exception as ex:
            print('Cannot create directory file')
            print(ex)
