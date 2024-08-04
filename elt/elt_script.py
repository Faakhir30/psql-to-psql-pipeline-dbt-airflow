import subprocess
import time


def wait_for_pg(host, max_tries= 3, delay_secs= 5):
    for i in range(max_tries):
        try:
            result = subprocess.run(
                ['pg_isready', '-h', host],
                check=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Postgres is ready")
                return True
        except subprocess.CalledProcessError as e:
            if i == max_tries - 1:
                print(f"Postgres is not ready after {max_tries} tries")
                return False
            print(f"Postgres is not ready, retrying in {delay_secs} seconds...")
            time.sleep(delay_secs)
    return False

if not wait_for_pg('source-postgres'):
    exit(1)
    
print("Postgres is ready, continuing with the script...")

source_config = {
    'host': 'source-postgres',
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret'
}

target_config = {
    'host': 'target-postgres',
    'dbname': 'target_db',
    'user': 'postgres',
    'password': 'secret'
}


dump_cmd = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'
]

subprocess_env = dict(PGPASSWORD=source_config['password'])

subprocess.run(dump_cmd, env=subprocess_env, check=True)

load_cmd = [
    'psql',
    '-h', target_config['host'],
    '-U', target_config['user'],
    '-d', target_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'
]

subprocess_env = dict(PGPASSWORD=target_config['password'])

subprocess.run(load_cmd, env=subprocess_env, check=True)

print("Data loaded successfully.")