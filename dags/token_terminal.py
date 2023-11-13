from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import os
import subprocess
import yaml
import h5py
import airflow.utils.dates


default_args = {"owner": "bohan", "retries": 10, "retry_delay": timedelta(hours=1)}


def create_daily_folder(ds):
    parsed_date = datetime.strptime(f"{ds}", "%Y-%m-%d")
    formate_date = parsed_date.strftime("%Y%m%d")
    directory_name = f"/remote/iosg/raw-2/buckets/feed.airflow.token_terminal/{formate_date}"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    h5_path = f"/remote/iosg/raw-2/buckets/feed.airflow.token_terminal/{formate_date}/{formate_date}_daily_matrix.h5"
    with h5py.File(h5_path, "w") as f:
        pass

def check_if_update(ds):
    parsed_date = datetime.strptime(f"{ds}", "%Y-%m-%d")
    formate_date = parsed_date.strftime("%Y%m%d")
    new_directotry ="/remote/iosg/home-2/bot-alpha-1/workspace/navi"
    os.chdir(new_directotry)
    command_1 = f"""./pyrunner python3/database/token_terminal/generate_index.py \
    check_matrix --date={formate_date}"""
    command_2 = f"""./pyrunner python3/database/token_terminal/generate_index.py \
    check_project --date={formate_date}"""
    result_1 = subprocess.run(command_1,shell=True,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    result_2 = subprocess.run(command_2,shell=True,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    print("result_1:",result_1.stdout.strip())
    print("result_2:",result_2.stdout.strip())
    print(result_1.stdout.strip() == "1")
    if result_1.stdout.strip() == "1" and result_2.stdout.strip() == "1":
        print("we successfully update the project and matrix")
    else: 
        print("we fail to update today's data,will retry one hour later")
        raise Exception("we fail to update today's data, will retry one hour later")

def update_index(ds):
    bound = datetime.strptime("2023-09-01", "%Y-%m-%d")
    parsed_date = datetime.strptime(f"{ds}", "%Y-%m-%d")
    data_string = parsed_date.strftime("%Y%m%d")
    if parsed_date >= bound:
        print("current time is:",data_string)
        new_directotry ="/remote/iosg/home-2/bot-alpha-1/workspace/navi"
        os.chdir(new_directotry)
        command = f"""./pyrunner python3/database/token_terminal/generate_index.py \
        get_update_index --date={data_string}"""
        result=subprocess.run(command,shell=True, check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        print(result.stderr)
        print(result.stdout)


def load_live_data(ds):
    bound = datetime.strptime("2023-06-01", "%Y-%m-%d")
    parsed_date = datetime.strptime(f"{ds}", "%Y-%m-%d")
    date_string = parsed_date.strftime("%Y-%m-%d")
    if parsed_date > bound:
        new_directotry ="/remote/iosg/home-2/bot-alpha-1/workspace/navi"
        os.chdir(new_directotry)
        command = f"""./pyrunner python3/database/token_terminal/load_live_data.py \
        load_live_data --date={date_string}"""
        print("command is ",command)
        result=subprocess.run(command,shell=True, check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        print(result.stderr)
        print(result.stdout)


def generate_index(ds):
    parsed_date = datetime.strptime(f"{ds}", "%Y-%m-%d")
    date_string = parsed_date.strftime("%Y%m%d")
    h5_file=f"/remote/iosg/raw-2/buckets/feed.airflow.token_terminal/{date_string}/{date_string}_daily_matrix.h5"
    new_directotry ="/remote/iosg/home-2/bot-alpha-1/workspace/navi"
    os.chdir(new_directotry)
    command = f"""./pyrunner python3/database/token_terminal/generate_matrix.py \
    generate_index_matrix --formate_date={date_string} --h5_file={h5_file}"""
    result=subprocess.run(command,shell=True,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True)
    print(result.stderr)
    print(result.stdout)


def generate_matrix(ds):
    parsed_date = datetime.strptime(f"{ds}", "%Y-%m-%d")
    date_string = parsed_date.strftime("%Y%m%d")
    date_string1 = parsed_date.strftime("%Y-%m-%d")
    h5_file=f"/remote/iosg/raw-2/buckets/feed.airflow.token_terminal/{date_string}/{date_string}_daily_matrix.h5"
    new_directotry ="/remote/iosg/home-2/bot-alpha-1/workspace/navi"
    os.chdir(new_directotry)
    command = f"""./pyrunner python3/database/token_terminal/generate_matrix.py \
    generate_matrix --formate_date={date_string1} --h5_file={h5_file}"""
    result=subprocess.run(command,shell=True, check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    print(result.stderr)
    print(result.stdout)

def send_slack(execution_date):
    new_directotry ="/remote/iosg/home-2/bot-alpha-1/workspace/navi"
    os.chdir(new_directotry)
    time = execution_date.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    print(time)
    command = f"""./pyrunner python3/database/token_terminal/generate_index.py \
    send_slack """
    result=subprocess.run(command,shell=True, check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)

with DAG(
    dag_id="token_terminal_matrix_dag",
    default_args=default_args,
    description="create daily folder and generate daily matrix",
    max_active_runs=1,
    schedule_interval = "0 14 * * *",
    start_date=datetime(2023, 11, 1)
) as dag:
    create_daily_folder = PythonOperator(
        task_id="create_daily_folder", 
        queue = "token_terminal_1",
        python_callable=create_daily_folder
    )
    check_if_update = PythonOperator(
        task_id="check_if_update", 
        queue = "token_terminal_1",
        python_callable=check_if_update
    )
    update_index = PythonOperator(
        task_id="update_index", 
        queue = "token_terminal_1",
        python_callable=update_index
    )
    load_live_data = PythonOperator(
        task_id="load_live_data", 
        queue = "token_terminal_1",
        python_callable=load_live_data
    )
    generate_index = PythonOperator(
        task_id="generate_index", 
        queue = "token_terminal_1",
        python_callable=generate_index
    )
    generate_matrix = PythonOperator(
        task_id="generate_matrix", 
        queue = "token_terminal_1",
        python_callable=generate_matrix
    )
    send_slack = PythonOperator(
        task_id = "send_slack",
        queue = "token_terminal_1",
        python_callable=send_slack
    )

    start = DummyOperator(task_id="start")

start >> create_daily_folder >> check_if_update >> update_index >> load_live_data >> generate_index >> generate_matrix >> send_slack