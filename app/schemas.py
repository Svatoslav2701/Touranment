from pydantic import BaseModel
from typing import List, Optional


# User schemas
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True



class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TeamOut(TeamBase):
    id: int
    description: Optional[str]
    players: List[UserOut] = []
    score: Optional[int] = 0

    class Config:
        orm_mode = True



class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None


class TournamentCreate(TournamentBase):
    pass


class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TournamentOut(TournamentBase):
    id: int
    is_finished: bool
    teams: List[TeamOut] = []

    class Config:
        orm_mode = True


# Result schemas
class ResultBase(BaseModel):
    team_id: int
    tournament_id: int
    score: int


class ResultCreate(ResultBase):
    pass


class ResultOut(ResultBase):
    id: int

    class Config:
        orm_mode = True



class AddPlayerToTeam(BaseModel):
    user_id: int


class RemovePlayerFromTeam(BaseModel):
    user_id: int
