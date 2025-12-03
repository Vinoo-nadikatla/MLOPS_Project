# MLOPS_Project — Build & Run

This project provides a FastAPI-based model API. This README explains how to build and run the project locally and with Docker (you mentioned Docker Desktop is installed).

**Quick summary**: the `Dockerfile` packages the runtime and the `src/app` code into a container and runs `uvicorn main:app`. The container expects a model file at the path provided by the `MODEL_PATH` environment variable (default `/app/models/model.pkl`). The image does not bake a model file by default — you can either mount your model into the container or modify the `Dockerfile` to copy it into the image.

**Contents**
- **Local**: run with a Python virtual environment and `uvicorn`.
- **Docker**: build with `docker build` or use `docker-compose` (already included).

---

**1) Build & run locally (PowerShell)**

Prerequisites: Python 3.10 and Git.

Open PowerShell at the repository root and run:

```powershell
# create virtualenv (once)
python -m venv .venv

# activate
.venv\Scripts\Activate.ps1

# install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# set MODEL_PATH if your model is at src/models/model.pkl
$env:MODEL_PATH = "$(Resolve-Path .\src\models\model.pkl)"

# run the API
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
```

If you don't have a trained model yet, run the training scripts in `src/models` or `flows/pipeline.py` to produce `model.pkl`, or copy a compatible joblib model to `src/models/model.pkl`.

**2) Build & run with Docker**

This project contains a `Dockerfile` that:

- uses `python:3.10-slim`
- installs Python dependencies from `requirements.txt`
- copies `src/app` into `/app`
- sets `ENV MODEL_PATH=/app/models/model.pkl`
- exposes port `8000` and runs `uvicorn main:app`

Because the Dockerfile as shipped copies only `src/app`, the model file is not included by default. Two common options:

- Mount the model directory from your host into the container (recommended during development).
- Copy the model into the image at build time (useful for demos). Edit `Dockerfile` to `COPY src/models /app/models` before building.

Example — build image then run mounting the local models directory (PowerShell):

```powershell
docker build -t mlops_project:latest .

# replace the host path if your model is elsewhere
docker run --rm -p 8000:8000 \
  -e MODEL_PATH=/app/models/model.pkl \
  -v "$(Resolve-Path .\src\models):/app/models" \
  mlops_project:latest
```

Note: on Windows use `Resolve-Path` or explicitly pass `D:/...` style paths in the `-v` argument. Use quotes around the path in PowerShell.

**3) Using docker-compose**

You can also run the service with `docker-compose` (already present):

```powershell
docker-compose up --build
# stop
docker-compose down
```

`docker-compose.yml` sets the container `MODEL_PATH` to `/app/models/model.pkl` and maps port `8000:8000`. You still need to ensure the model exists inside the container (via mount or Dockerfile copy).

**4) Troubleshooting**

- If startup logs show `Could not load model: ...`, verify the model exists at the path in the container (`$env:MODEL_PATH`).
- Confirm the model was saved with `joblib` and is compatible with the `scikit-learn` version in `requirements.txt`.
- If dependencies change, rebuild the Docker image.

**5) Next steps / suggestions**

- If you'd like, I can modify the `Dockerfile` to copy `src/models` into the image (handy for demos), or add health endpoints.
- I also added helper PowerShell scripts in `scripts/` to make starting locally and with Docker easier.

---

Files changed/added:
- `README.md` (this file)
- `scripts/start-local.ps1` (helper to start the app locally)
- `scripts/start-docker.ps1` (helper to build and run the container with a mounted model)

If you want the model to be baked into the image instead, tell me and I'll update the `Dockerfile` to copy `src/models` into `/app/models` and show the exact rebuild commands.
# MLOPS_Project
This project implements a complete end-to-end MLOps pipeline using only local, open-source tools. It covers the full lifecycle of a machine learning system — from data ingestion to deployment and monitoring. Key components include DVC for data/version tracking, MLflow for experiment management, Prefect for workflow orchestration, Docker for containerised deployment, FastAPI/Streamlit for local serving, and Evidently AI for monitoring and drift detection. This repository demonstrates how to build a fully reproducible, automated, and production-ready ML workflow on a local machine.
