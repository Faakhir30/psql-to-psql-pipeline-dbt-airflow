FROM apache/airflow:2.0.1

# Install additional packages
RUN pip install apache-airflow-providers-docker