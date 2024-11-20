# INF6103_Final_Project

In order to deploy this project, you must make sure to have a powerful enough machine (>32GB RAM) with Docker and Docker Compose installed.

```bash
# 1. Clone the project
git clone https://github.com/IkramKo/INF6103_Final_Project.git

# 2. Go to deployment folder
cd deployment

# 3. Deploy the simulation using Docker Compose
docker compose up --build -d

# 4. Grafana should now be accessible on port 3000
```
