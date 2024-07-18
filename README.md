# FastAPI JWT Auth (Basic)

### Authentication and authorization using FastAPI + PyJWT + Microservices

### Setting up the Environment

Create a `.env` file with the following content both globally and in each service directory:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=postgres
DATABASE_URL=postgresql+asyncpg://postgres:password@auth_db:5432/postgres
```

### Running the Application

To start the application, run the following command:

```shell
docker-compose up
```

### Applying Linters and Formatters

To apply all linters and formatters, run the following command:

```shell
pre-commit run --all-files
```

### Creating a New Service

To create a new service, use the following command:

```shell
make create-service service=<service_name>
```
