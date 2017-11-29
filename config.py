import logging
from ConfigParser import ConfigParser
from db import Database
import argparse


def initParser():
    parser = argparse.ArgumentParser(description="Parses job-output.json.gz\
                                     files for step durations.")
    parser.add_argument('--settings', dest='settings_file',
                        help="path to settings file")
    parser.add_argument('filename', help="path to file to scan")

    args = parser.parse_args()
    return args


def initConfig(filename):
    config = ConfigParser()
    config.read(filename)
    return config


def initLogging(config):
    FORMAT = "%(asctime)-15s %(message)s"
    # configure sqlalchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

    levels = [logging.WARN, logging.INFO, logging.DEBUG]
    level = levels[config.getint('logging', 'verbosity')]

    # configure app logging
    logging.basicConfig(filename=config.get('logging', 'file'),
                        level=level,
                        format=FORMAT,
                        datefmt='%Y-%m-%d %H:%M:%S%Z')


def initDatabase(config):
    db = Database()
    db_engine = config.get('database', 'engine', 'sqlite')
    if db_engine == 'mysql':
        connection_string = 'mysql+pymysql://%s:%s@%s/%s' % (
            config.get('database', 'username'),
            config.get('database', 'password'),
            config.get('database', 'uri'),
            config.get('database', 'dbname'))
    elif db_engine == 'sqlite':
        connection_string = 'sqlite:///%s' % (
            config.get('database', 'uri'))
    else:
        print "database engine not supported"
        return 1

    db.connect(connection_string)
    return db
