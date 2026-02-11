# TFB_Grupo4
Proyecto de GitHub del Grupo4. Conformado por Iria Moreno Pinto y Javier Moreno Martin.

## Deployment with Docker (Recommended)
The deployment of the project is made with docker compose to start the API (FastAPI + Uvicorn) and MongoDB.

## Basic Requirements

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

### Build and Run

From the root of the project, execute:
docker compose up --build

With this command we build the API Docker image, start the API and MongoDB Contiainers and automatically create the required collections and indexes on startup of the DB.

### Access the API

Once running, the API will be available at http://localhost:8000. You can check the implementations in Swagger UI.

- Swagger UI: http://localhost:8000/docs  

### Stop the Deployment

To stop the containers:

docker compose down


If you also want to remove volumes (including MongoDB data):

docker compose down -v