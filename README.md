## 🚀 Quickstart

This project spins up an Apache Airflow–driven ETL pipeline (in Docker) that fetches current weather data from Weatherstack and loads it into a PostgreSQL database.

### 1. Prerequisites

- **Docker** & **Docker Compose**  
  Verify by running:  
  ```bash
  docker compose version
- **Weatherstack** API key

Visit: https://weatherstack.com/dashboard

Sign up / log in, then copy your Access Key.

### 2. Fetch the Official Airflow docker-compose.yaml
Create and enter a new project folder:

- mkdir my-etl-project
- cd my-etl-project

- Download Airflow’s Docker Compose setup: \
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.0.0/docker-compose.yaml'

### 3. Create Required Directories & Environment File \
   ```bash
    mkdir -p ./dags ./logs ./plugins ./config \
    echo -e "AIRFLOW_UID=$(id -u)" > .env \
   ```

- **dags/**: your DAG definitions
- **logs/**: Airflow task logs
- **plugins/**: custom operators/hooks
- **config/**: your config.json

### 4. Configure dag_utils/config.json
- Use host.docker.internal to connect from Airflow containers to your local PostgreSQL.

- Replace placeholder values with your actual credentials.

- You can configure the config.json file to specify which cities' weather data should be fetched and loaded into PostgreSQL.

### 5. Initialize & Start Airflow
Initialize the database & create default users:
   ```bash
    docker compose up airflow-init 
   ```

Start all services:
   ```bash
    docker compose up
   ```



### 6. Verify & Access
Airflow Web UI: http://localhost:8080

Log in using the default credentials (unless overridden):
   ```bash
    Username: airflow
    Password: airflow
   ```

### 7. Next Steps
Drop your DAG files into dags/.

Customize your ETL logic to fetch from Weatherstack’s API and load into Postgres. 

🐘 PostgreSQL Output Preview
Here’s a snapshot of the data loaded into PostgreSQL:

<img width="1143" alt="Screenshot 2025-05-05 at 22 23 19" src="https://github.com/user-attachments/assets/1de0a28c-9dd6-45b9-84e9-919b55ebae39" />


