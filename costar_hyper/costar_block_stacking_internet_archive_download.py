import internetarchive
import argparse
import os


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Download the dataset from the Internet Archive.')
    parser.add_argument(
        "--path", type=str,
        default=os.path.join(os.path.expanduser("~"),
                             '.keras/datasets/costar_block_stacking_dataset_v0.4/'),
        help='The path to download the dataset to. '
             'Default is "~/.keras/datasets/costar_block_stacking_dataset_v0.4/"')
    parser.add_argument(
        "--dryrun", action='store_true', default=False,
        help='Use this flag to only do a test download of the files from the internet archive')


def main(args, root='root'):
    item = internetarchive.get_item('johns_hopkins_costar_dataset')

    path = os.path.expanduser(args['path'])

    dryrun = args['dryrun']

    r = item.download(
            destdir=path,  # The directory to download files to
            ignore_existing=True,  # Skip files that already exist locally
            checksum=True,  # Skip files based on checksum
            verbose=True,  # Print progress to stdout
            retries=100,  # Thenumber of times to retry on failed requests
            # Set to true to print headers to stdout, and exit without downloading
            dryrun=dryrun)

    print(r)


if __name__ == '__main__':
    args = _parse_args()
    main(args)
