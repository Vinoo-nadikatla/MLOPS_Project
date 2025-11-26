from prefect import flow, task
import subprocess

@task
def sync_git_and_dvc():
    # fetch all branches to allow dvc git-remote access
    subprocess.run(["git", "fetch", "--all"], check=True)
    subprocess.run(["dvc", "pull"], check=True)

@task
def run_dvc_repro():
    subprocess.run(["dvc", "repro"], check=True)

@task
def build_docker_image():
    subprocess.run(["docker", "build", "-t", "heart-api:latest", "."], check=True)

@task
def launch_containers():
    subprocess.run(["docker-compose", "up", "-d"], check=True)

@flow
def full_pipeline():
    sync_git_and_dvc()
    run_dvc_repro()
    build_docker_image()
    launch_containers()

if __name__ == "__main__":
    full_pipeline()
