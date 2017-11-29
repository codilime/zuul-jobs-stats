#!/usr/bin/env python
from logentry import LogEntry
from config import initConfig, initDatabase, initLogging, initParser
from os.path import exists
import logging


def main():
    args = initParser()
    config = initConfig(args.settings_file)
    db = initDatabase(config)
    initLogging(config)

    if exists(args.filename):
        log_entry = LogEntry(args.filename)
        db.insert_entry(log_entry)
        return 0
    else:
        logging.error("%s does not exist. Exiting..." % args.filename)
        return 1


if __name__ == '__main__':
    exit(main())
