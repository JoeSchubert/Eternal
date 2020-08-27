from sqlalchemy import Column, Integer, String, create_engine, or_, and_, between, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///eternal_bot.db', echo=False)

Session = sessionmaker(bind=engine)
session = Session()


# Helper function to get all rows
def raid_all():
    return session.query(Raids)


# Helper function to get existing entry for corp
def raid_for_corp(corp):
    return session.query(Raids).filter_by(corp=corp).first()


# Helper function to get existing entry for corp
def rename_corp(corp, new_name):
    raid = raid_for_corp(corp)
    if raid:
        raid.corp = new_name
        session.add(raid)
        session.commit()
        return True
    else:
        return False


# Helper function to add or update information about a raid
def raid_add(corp, day_of_week, time, systems):
    raid = raid_for_corp(corp)
    if raid:
        raid.corp = raid.corp
        raid.day_of_week = day_of_week
        raid.time = time
        if not systems:
            raid.systems = raid.systems
        else:
            sys = list(set(raid.systems.split(",") + systems))
            sys.sort()
            raid.systems = ",".join(sys)
    else:
        sys = list(set(systems))
        sys.sort()
        sys = ",".join(sys)
        raid = Raids(corp=corp, day_of_week=day_of_week, time=time, systems=sys)
    session.add(raid)
    session.commit()


# Helper function to delete a system for a corp
def raid_remove_sys(corp, systems):
    raid = raid_for_corp(corp)
    if raid:
        raid.corp = raid.corp
        raid.day_of_week = raid.day_of_week
        raid.time = raid.time
        sys = raid.systems.split(",")
        if isinstance(systems, list):
            for x in systems:
                sys.remove(x.strip())
        else:
            sys.remove(systems.strip())
        raid.systems = ",".join(sys)
    session.commit()


# Helper function to add a system for a corp
def raid_add_sys(corp, systems):
    raid = raid_for_corp(corp)
    if raid:
        raid.corp = raid.corp
        raid.day_of_week = raid.day_of_week
        raid.time = raid.time
        sys = raid.systems.split(",")
        if isinstance(systems, list):
            for x in systems:
                sys.append(x.strip())
        else:
            sys.append(systems.strip())
        raid.systems = ",".join(sys)
    session.commit()


# Helper function to delete corp raids
def raid_del_corp(corp):
    count = session.query(Raids).filter_by(corp=corp).delete()
    session.commit()
    return count


# Helper function get raids by weekday
def raids_by_day(weekday):
    return session.query(Raids).filter(func.lower(Raids.day_of_week) == weekday.lower())


# Helper function to get raids in a certain amount of time
def raids_by_time(start, end):
    start_tokens = start.split(" ")
    end_tokens = end.split(" ")
    if start_tokens[0] == end_tokens[0]:
        return session.query(Raids).filter(and_(Raids.day_of_week == start_tokens[0], between(Raids.time,
                                                                                              start_tokens[1],
                                                                                              end_tokens[1])))
    else:
        return session.query(Raids).filter(or_(
            and_(Raids.day_of_week == start_tokens[0], Raids.time >= start_tokens[1]),
            and_(Raids.day_of_week == end_tokens[0], Raids.time <= end_tokens[1])))


class Raids(Base):
    __tablename__ = 'raids'

    id = Column(Integer, primary_key=True)
    corp = Column(String, unique=True)
    day_of_week = Column(String)
    time = Column(String)
    systems = Column(String)

    def __repr__(self):
        return "<Raids(corp='%s', day_of_week'%s', time='%s', systems='%s')>" % (
            self.corp, self.day_of_week, self.time, self.systems)


Base.metadata.create_all(engine)
