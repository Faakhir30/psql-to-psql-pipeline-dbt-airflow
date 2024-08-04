from datetime import datetime, timedelta
import subprocess
from airflow import DAG
from docker.types import Mount
from airflow.operators.python_operator import PythonOperator
from airflow.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

def run_elt_script():
    print('Running ELT script...')
    script_path = "/opt/airflow/elt/elt_script.py"
    result  = subprocess.run(['python', script_path],
                             capture_output=True,
                             text=True
                             )
    if result.returncode != 0:
        raise ValueError(f"ELT script failed: {result.stderr}")
    else:
        print(result.stdout)
    
dag = DAG(
    'elt_dbt_dag',
    default_args=default_args,
    description='ELT pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False
)

t1 = PythonOperator(
    task_id='run_elt_script',
    python_callable=run_elt_script,
    dag=dag
)

t2 = DockerOperator(
    task_id='run_dbt',
    image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
    api_version='auto',
    auto_remove=True,
    command='run --profiles-dir /root --project-dir /dbt',
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    mounts=[
        Mount(target='/root', source='~/.dbt', type='bind'),
        Mount(target='/dbt', source='~/workspaces/de/hollywood_data_pipeline/custom_postgres', type='bind'),
        ],
    dag=dag
)

t1 >> t2