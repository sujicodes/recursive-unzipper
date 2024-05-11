#!/usr/bin/env python

import argparse
import os
import zipfile
import rarfile
import tarfile
import logging


def parser_args():

    parser = argparse.ArgumentParser(
        description="scans for any archive files in the given path and after exctrating keeps checking again until no zip files are found",
        usage="usage: r_unarchive <path to scan>",
    )
    parser.add_argument("path", help="the path to scan archive", nargs="+")
    parser.add_argument("--chmod", help="chmods the extracted zip folders recursivley")
    parser.add_argument(
        "-v", "--verbose", help="prints out what is being done", action="store_true"
    )

    return parser.parse_args()


def chmod_recursively(path, permission_mode):
    """
    changes permission recursively

    Args:
        source_paths(list): paths
    """
    command = ["chmod", "-R", permission_mode, path]
    logger.info("Running: {}".format(command))

    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    out, err = p.communicate()
    if p.returncode:
        raise OSError("Couldnt chmod file :{0} \n Error: {1}".format(path, err))


def try_extract(path, destination_path, logger):
    """
    extracts archive file if the
    the file given is an archive file
    """
    try:
        if path.lower().endswith(".zip"):
            logger.info("Found ZIP file: {}".format(path))
            archive = zipfile.ZipFile(path, "r")
        elif path.lower().endswith(".rar"):
            logger.info("Found RAR file: {}".format(path))
            archive = rarfile.RarFile(path, "r")
        elif path.lower().endswith((".tar", "tar.gz", ".tgz", ".tar.bz", ".tar.xz")):
            logger.info("Found TAR file: {}".format(path))
            archive = tarfile.open(path)
        else:
            return False
    except (zipfile.BadZipfile, rarfile.NotRarFile, tarfile.ReadError):
        return False

    logger.info("Extracting...")
    archive.extractall(destination_path)
    archive.close()
    logger.info("Extracted in: {}".format(destination_path))
    return True


def unzip_recursively(source_paths, chmod=None, logger=None):
    """
    checks for any archive files in the
    given path and after exctracting keeps
    checking again until no zip files are found

    Args:
        source_path(list): path to check for any archives
    """
    for source_path in source_paths:
        if not os.path.isdir(source_path):
            raise TypeError("Not a directory")

        folder_queue = [source_path]
        for path in folder_queue:
            for root, dirs, files in os.walk(path):
                for file_ in files:
                    file_path = os.path.join(root, file_)
                    out_path = os.path.splitext(file_path)[0]
                    if try_extract(file_path, os.path.dirname(out_path), logger):
                        folder_queue.append(out_path)
                        if chmod:
                            chmod_recursively(out_path, int(chmod, 8))
                        logger.info("\n")


def main():

    args = parser_args()
    logger = logging.getLogger()
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.CRITICAL)

    if args.verbose:
        logger.setLevel(logging.INFO)

    unzip_recursively(args.path, args.chmod, logger)


if __name__ == "__main__":
    main()
