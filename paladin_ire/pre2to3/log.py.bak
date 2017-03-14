# -*- coding: utf-8 -*-

import logging

import logging
import os,sys

def setup_logger(args):

    def __file_logging(logger,fpath=os.path.join(os.path.dirname(__file__),
                                                 args.logpath)):
        fpath = _resolve_path(fpath)
        fmt = logging.Formatter('%(asctime)s %(threadName)-8s :: %(message)s')
        file_handler = logging.FileHandler(fpath,'a')
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logger.level)
        logger.addHandler(file_handler)

    def _get_level():
        if args.silent and args.logging and not args.debug:
            return logging.DEBUG
        if args.debug:
            return logging.DEBUG
        if args.verbose:
            return logging.INFO
        return logging.WARNING

    def _touch(fpath):
        if not os.path.exists(fpath):
            with open(fpath, 'w+') as f:
                return True
        return False

    def _resolve_path(fpath):
        # Convert to absolute path, touch file
        fpath = os.path.realpath(fpath)
        result = _touch(fpath)
        return fpath

    logger = logging.getLogger('paladin-ire')
    logger.setLevel(_get_level())

    if args.logging:
        params = (logger,args.logpath,)
        __file_logging(*params)

    return logger
