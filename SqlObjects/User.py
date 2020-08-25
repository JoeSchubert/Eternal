from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///eternal_bot.db')

Session = sessionmaker(bind=engine)
session = Session()


# Helper function to add to a user's history
def history_add(discord_id, server_id, event, user_name, timestamp):
    user = History(discord_id=discord_id, server_id=server_id, event=event, user_name=user_name, timestamp=timestamp)
    session.add(user)
    session.commit()


# Helper function to get number of joins
def history_joins(user_id):
    return session.query(History).filter_by(discord_id=user_id, event="join")


# Helper function to get previous nicks
def history_nicks(user_id):
    return session.query(History).filter_by(discord_id=user_id, event="nick_change")


class History(Base):
    __tablename__ = 'user_history'

    id = Column(Integer, primary_key=True)
    discord_id = Column(String)
    server_id = Column(String)
    event = Column(String)
    user_name = Column(String)
    timestamp = Column(String)

    def __repr__(self):
        return "<User(discord_id='%s', server_id'%s', event='%s', user_name='%s', timestamp='%s')>" % (
            self.discord_id, self.server_id, self.event, self.user_name, self.timestamp)


# Helper function to add a toon to a user
def toon_add(discord_id, server_id, character, timestamp):
    toon = session.query(Toon).filter_by(character=character).first()
    if not toon:
        toon = Toon(discord_id=discord_id, server_id=server_id, character=character, timestamp=timestamp)
    session.add(toon)
    session.commit()


# Helper function to search toons
def toon_search(toon):
    return session.query(Toon).filter_by(character=toon)


# Helper function to search toons by user
def toon_search_by_user(discord_id):
    return session.query(Toon).filter_by(discord_id=discord_id)


# Helper function to get delete a toon
def toon_delete(toon):
    results = session.query(Toon).filter_by(character=toon).delete()
    session.commit()
    return results


# Helper function to delete all toons for user
def toon_delete_for_user(user):
    results = session.query(Toon).filter_by(discord_id=user).delete()
    session.commit()
    return results


class Toon(Base):
    __tablename__ = 'user_characters'

    id = Column(Integer, primary_key=True)
    discord_id = Column(String, nullable=False)
    server_id = Column(String)
    character = Column(String, unique=True, nullable=False)
    timestamp = Column(String)

    def __repr__(self):
        return "<User(discord_id='%s', server_name='%s', event='%s', user_name='%s', timestamp='%s')>" % (
            self.discord_id, self.server_name, self.event, self.user_name, self.timestamp)


Base.metadata.create_all(engine)
