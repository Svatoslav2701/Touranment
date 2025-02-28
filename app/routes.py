from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, auth
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .auth import decode_access_token
from .database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, auth
from .middlewares import verify_token  

router = APIRouter()



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/register", status_code=201)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "JWT"}

@router.get("/tournaments/")
def get_tournaments(db: Session = Depends(get_db),token_data: dict = Depends(verify_token)):
    tournaments = db.query(models.Tournament).all()
    response = []
    for tournament in tournaments:
        response.append({
            "id": tournament.id,
            "name": tournament.name,
            "teams_count": len(tournament.teams)
        })
    return response

@router.post("/tournaments/", status_code=201)
def create_tournament(
    tournament: schemas.TournamentCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)  
):
    user_email = token_data.get("sub")
    owner = db.query(models.User).filter(models.User.email == user_email).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    db_tournament = models.Tournament(name=tournament.name, owner_id=owner.id) 
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament



@router.get("/tournaments/{tournament_id}/")
def get_tournament_detail(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    teams = sorted(
        tournament.teams,
        key=lambda team: sum(res.score for res in team.results),
        reverse=True
    )
    return {
        "id": tournament.id,
        "name": tournament.name,
        "is_finished": tournament.is_finished,
        "teams": [
            {
                "name": team.name,
                "score": sum(res.score for res in team.results)
            }
            for team in teams
        ]
    }


@router.put("/tournaments/{tournament_id}/")
def update_tournament(tournament_id: int, tournament_update: schemas.TournamentUpdate, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament.name = tournament_update.name or tournament.name
    db.commit()
    return {"message": "Tournament updated successfully"}


@router.delete("/tournaments/{tournament_id}/")
def delete_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    db.delete(tournament)
    db.commit()
    return {"message": "Tournament deleted successfully"}


@router.post("/tournaments/{tournament_id}/add_team/{team_id}/")
def add_team_to_tournament(tournament_id: int, team_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not tournament or not team:
        raise HTTPException(status_code=404, detail="Tournament or team not found")
    
    tournament.teams.append(team)
    db.commit()
    return {"message": f"Team {team.name} added to tournament {tournament.name}"}



@router.post("/tournaments/{tournament_id}/finish/")
def finish_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(models.Tournament).filter(models.Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament.is_finished = True
    db.commit()
    return {"message": f"Tournament {tournament.name} is finished"}


@router.post("/teams/", status_code=201)
def create_team(team: schemas.TeamCreate, user_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user_email = user_data.get("sub")
    owner = db.query(models.User).filter(models.User.email == user_email).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found")

    
    existing_team = db.query(models.Team).filter(models.Team.name == team.name).first()
    if existing_team:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team with this name already exists")



    new_team = models.Team(name=team.name, owner_id=owner.id)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    
    new_player = models.Player(name=owner.username, team_id=new_team.id)
    db.add(new_player)
    db.commit()

    return {"message": f"Team {new_team.name} created successfully with owner {owner.username}"}



@router.get("/teams/")
def get_teams(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    response = []
    for team in teams:
        score = sum(res.score for res in team.results)
        response.append({
            "id": team.id,
            "name": team.name,
            "players_count": len(team.players + 1),
            "results": score,
        })
    return response


@router.get("/teams/{team_id}")
def get_team_by_id(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    return {
        "id": team.id,
        "name": team.name,
        "results": team.results,
        "players": [
            {"id": player.id, "name": player.name} for player in team.players
        ]  
    }



@router.put("/teams/{team_id}/")
def update_team(team_id: int, team_update: schemas.TeamUpdate, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.name = team_update.name or team.name
    db.commit()
    return {"message": "Team updated successfully"}


@router.delete("/teams/{team_id}/")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully"}


@router.post("/results", status_code=201)
def add_result(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == result.team_id).first()
    tournament = db.query(models.Tournament).filter(models.Tournament.id == team.tournament_id).first()
    if tournament.is_finished:
        return {"message": "Tournament is finished"}
    db_result = models.Result(team_id=result.team_id, score=result.score)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@router.get("/ranking")
def get_ranking(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    results = db.query(models.Result).all()
    ranking = {}
    for team in teams:
        team_score = sum(res.score for res in results if res.team_id == team.id)
        ranking[team.name] = team_score
    return ranking

@router.post("/teams/{team_id}/add_player")
def add_player_to_team(team_id: int, player: schemas.AddPlayerToTeam, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    decoded_token = decode_access_token(token)
    if not decoded_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_email = decoded_token.get("sub")
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    owner = db.query(models.User).filter(models.User.id == team.owner_id).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner of the team not found")
    if owner.email != user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the team owner can add players")
    
    player_user = db.query(models.User).filter(models.User.id == player.user_id).first()
    if not player_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    
    if player_user in team.players:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Player is already in the team")
      
    existing_team = db.query(models.Team).filter(models.Team.name == team.name).first()
    team_member_count = db.query(models.Player).filter(models.Player.team_id == existing_team.id).count() if existing_team else 0
    if team_member_count == 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Team can have no more than 5 members (including the owner)")
    
    db_players = models.Player(name=player_user.username, team_id=team.id)
    db.add(db_players)
    db.commit()
    return {"message": f"Player {player_user.username} added to team {team.name}"}



@router.delete("/teams/{team_id}/remove_player")
def remove_player_from_team(
    team_id: int, player: schemas.RemovePlayerFromTeam, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    
    decoded_token = decode_access_token(token)
    if not decoded_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_email = decoded_token.get("sub")
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    owner = db.query(models.User).filter(models.User.id == team.owner_id).first()
    
    if owner.email != user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the team owner can remove players")

    player_user = db.query(models.User).filter(models.User.id == player.user_id).first()
    
    if not player_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    
    player_in_team = db.query(models.Player).filter(models.Player.name == player_user.username, models.Player.team_id == team.id).first()
    
    if not player_in_team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player is not in the team")
    
    
    db.delete(player_in_team)
    db.commit()

    return {"message": f"Player {player_user.username} removed from team {team.name}"}


