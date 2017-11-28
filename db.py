from sqlalchemy import Column, ForeignKey, Integer, Time, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import IntegrityError
import logging

Base = declarative_base()


class Build(Base):
    __tablename__ = 'build'
    id = Column(Integer, primary_key=True)
    label = Column(String(32), nullable=False, unique=True)
    date = Column(DateTime)


class Step(Base):
    __tablename__ = 'step'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)


class BuildStepTime(Base):
    __tablename__ = 'build_step_time'
    id = Column(Integer, autoincrement=True)
    step_id = Column(Integer, ForeignKey('step.id'), primary_key=True)
    build_id = Column(Integer, ForeignKey('build.id'), primary_key=True)
    time = Column(Time)

    step = relationship(Step)
    build = relationship(Build)


class Database():
    __engine = None
    __session = None

    def __init_schema(self):
        Base.metadata.create_all(self.__engine)

    def connect(self, connection_string, echo=False):
        self.__engine = create_engine(connection_string, echo=echo)
        if not database_exists(self.__engine.url):
            create_database(self.__engine.url)
        self.__init_schema()
        self.__session = sessionmaker(bind=self.__engine)()

    def get_existing(self, column, value):
        return self.__session.query(column.class_).filter(column == value).first()

    def insert_entry(self, log_entry):
        session = self.__session
        # Insert build entry if it doesn't exist
        build = self.get_existing(Build.label, log_entry.build_id)
        if not build:
            action = 'ADD'
            build = Build(label=log_entry.build_id, date=log_entry.date)
            session.add(build)
            session.commit()
        else:
            action = 'SKIP'
        logging.info('[%4s] Build %s: %s' % (action, build.date, build.label))

        # Insert step entry if it doesn't exist
        for step_name, time in log_entry.steps_times:
            step = self.get_existing(Step.name, step_name)
            action = 'SKIP'
            if not step:
                action = 'ADD'
                step = Step(name=step_name)
                session.add(step)
                session.commit()
            logging.info('[%4s] Step %s' % (action, step.name,))

            # Insert entry for each (step_name, time)
            try:
                build_step_time = BuildStepTime(build=build,
                                                step=step,
                                                time=time)
                session.add(build_step_time)
                session.commit()

            # Or skip if it already exists
            except IntegrityError:
                session.rollback()
                action = 'SKIP'
            else:
                action = 'ADD'

            logging.info("[%4s] Entry %s: %s (%s)" % (action, log_entry.build_id, step_name, time))


if __name__ == "__main__":
    db = Database()
    db.connect('sqlite:///build_step_times.db', True)
