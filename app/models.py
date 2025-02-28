from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)  
    email = Column(String, nullable=False, unique=False)                   
    hashed_password = Column(String, nullable=False)  
    tournaments = relationship("Tournament", back_populates="owner")
    teams = relationship("Team", back_populates="owner")

class Tournament(Base):
    __tablename__ = 'tournaments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="tournaments")
    teams = relationship("Team", back_populates="tournament")
    is_finished = Column(Boolean, default=False)

class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    score = Column(Integer, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', back_populates='results')


class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="teams")
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    tournament = relationship("Tournament", back_populates="teams")
    results = relationship('Result', back_populates='team')
    players = relationship('Player', back_populates='team')

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', back_populates='players')

team_tournaments = Table(
    "team_tournaments",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("tournament_id", Integer, ForeignKey("tournaments.id"), primary_key=True),
)