Tournament Management API

Project Description

This project is an API for managing tournaments and teams.
Built with FastAPI, using PostgreSQL and JWT authentication.

📌 API Features:

User registration and authentication (JWT tokens).

Create, update, delete tournaments.

Add teams to tournaments.

Manage teams and players.

Record match results.

Calculate team rankings.

🔧 Installation and Running (Docker)

1️⃣ Clone the Repository

git clone https://github.com/Svatoslav2701/Touranment.git
cd Touranment

2️⃣ Run with Docker

Create a .env file (or use .env.example):

DATABASE_URL=postgresql://postgres:mypassword@db:5432/tournament_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

Build and start the containers:

docker-compose up --build -d

Apply migrations:

docker-compose exec app alembic upgrade head

API will be available at:👉 http://localhost:8000/docs

⚙️ API Endpoints

🔐 Authentication

POST /register — User registration

POST /login — User login and token retrieval

🏆 Tournaments

GET /tournaments — Get a list of tournaments

POST /tournaments — Create a tournament

GET /tournaments/{id} — Get tournament details

PUT /tournaments/{id} — Update a tournament

DELETE /tournaments/{id} — Delete a tournament

POST /tournaments/{id}/teams/{team_id} — Add a team to a tournament

POST /tournaments/{id}/finish — Finish a tournament

⚽ Teams

GET /teams — Get a list of teams

POST /teams — Create a team

GET /teams/{id} — Get team details

PUT /teams/{id} — Update a team

DELETE /teams/{id} — Delete a team

POST /teams/{id}/players — Add a player to a team

🏅 Results

POST /results — Add a match result

GET /ranking — Get team rankings

📖 API Documentation (Swagger)

The API includes interactive documentation powered by Swagger and Redoc.
Once the project is running, you can access it here:

Swagger UI: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

🛠 Technologies

FastAPI — API framework.

SQLite — Database.

Alembic — Database migrations.

Docker & Docker Compose — Containerized deployment.

JWT (JSON Web Token) — User authentication.

🚀 Author

Developed by Svatoslav2701.📧 Contact: lukashenkosviatoslav2701@gmail.com
