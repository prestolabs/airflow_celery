from airflow import DAG
from datetime import datetime,timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
import os
import subprocess
import yaml
import airflow.utils.dates



default_args = {
    "owner":"bohan",
    "retries":5,
    "retry_delay":timedelta(minutes=2)
}

def binance_top100(ds):
    print(os.getcwd())
    new_directotry ="/remote/iosg/home-2/bohan/workspace/fastfeature/coinstrat"
    os.chdir(new_directotry)
    print("current dir is ",os.getcwd())
    parsed_date=datetime.strptime(f"{ds}","%Y-%m-%d")
    format_date=int(parsed_date.strftime("%Y%m%d"))
    print(format_date)
    adjust_config(format_date,"binance_top100")
    command_5="./pyrunner coinstrat/strat_lm/app/alpha/research/bohan/pysim/main.py -c \
    coinstrat/strat_lm/app/alpha/research/bohan/pysim/configs/config_for_weekly_job/config_coin_binance_top100.yml --data-only"
    result=subprocess.run(command_5,shell=True,capture_output=True, text=True)
    print(result.stderr)
    print(result.stdout)

def binance_top50(ds):
    print(os.getcwd())
    new_directotry ="/remote/iosg/home-2/bohan/workspace/fastfeature/coinstrat"
    os.chdir(new_directotry)
    print("current dir is ",os.getcwd())
    parsed_date=datetime.strptime(f"{ds}","%Y-%m-%d")
    format_date=int(parsed_date.strftime("%Y%m%d"))
    print(format_date)
    adjust_config(format_date,"binance_top50")
    command_5="./pyrunner coinstrat/strat_lm/app/alpha/research/bohan/pysim/main.py -c \
    coinstrat/strat_lm/app/alpha/research/bohan/pysim/configs/config_for_weekly_job/config_coin_binance_top50.yml --data-only"
    result=subprocess.run(command_5,shell=True,capture_output=True, text=True)
    print(result.stderr)
    print(result.stdout)

def adjust_config(date,name):
    file_name=f"/remote/iosg/home-2/bohan/workspace/fastfeature/coinstrat/coinstrat/strat_lm/app/alpha/research/bohan/pysim/configs/config_for_weekly_job/config_coin_{name}.yml"
    cache_path=f"./{name}"
    with open (file_name,"r") as file:
        contents = yaml.safe_load(file)
        contents["reader"]["end_date"] = date
        contents["reader"]["cache_path"] = cache_path
    
    with open (file_name,"w") as file:
        yaml.dump(contents,file,sort_keys=False)

def adjust_config_pnl(name,alpha,date):
    file_name=f"/remote/iosg/home-2/bohan/workspace/fastfeature/coinstrat/coinstrat/strat_lm/app/alpha/research/bohan/pysim/configs/config_for_weekly_job/config_coin_{name}.yml"
    template_path=f"/remote/iosg/home-2/bohan/workspace/midfreq_conf/team_alpha/production/alphas/5m/{alpha}/config.xml"
    export_path=f"/remote/iosg/home-2/bohan/workspace/buckets/pnl/{name}/{alpha}"
    name_path=f"/remote/iosg/home-2/bohan/workspace/buckets/pnl/{name}/"
    if not os.path.exists(name_path):
        os.mkdir(name_path)
    else:
        pass

    if not os.path.exists(export_path):
        os.mkdir(export_path)
    else:
        pass
    export_config_path=f"/remote/iosg/home-2/bohan/workspace/buckets/pnl/{name}/{alpha}/config.yml"
    with open (file_name,"r") as file:
        contents = yaml.safe_load(file)
        contents["template"]["path"] = template_path
        contents["sim"]["export"]["path"] = export_path
    with open (export_config_path,"w") as file:
        yaml.dump(contents,file,sort_keys=False)
    with open (export_config_path,"r") as file:
        print("here is the template path:",contents["template"]["path"])


def pnl_generation(ds,**kwargs):
    print(os.getcwd())
    new_directotry ="/remote/iosg/home-2/bohan/workspace/fastfeature/coinstrat"
    os.chdir(new_directotry)
    parsed_date=datetime.strptime(f"{ds}","%Y-%m-%d")
    format_date=int(parsed_date.strftime("%Y%m%d"))
    name=kwargs["name"]
    alpha=kwargs["alpha"]
    compare_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
    if parsed_date < compare_date and (name == "bybit_top50" or name == "bybit_top80" or name == "okex_top50" or name == "okex_top80"):
        pass
    else:
        print("current dir is ",os.getcwd())
        adjust_config_pnl(name,alpha,format_date)
        command_5=f"./pyrunner coinstrat/strat_lm/app/alpha/research/bohan/pysim/main.py -c \
        /remote/iosg/home-2/bohan/workspace/buckets/pnl/{name}/{alpha}/config.yml"
        result=subprocess.run(command_5,shell=True,capture_output=True, text=True)
        print(result.stderr)
        print(result.stdout)


with DAG(
    dag_id = "5min_binance_alpha_pnl_generation_dag",
    default_args=default_args,
    description="generate 5min research, then generate pnl",
    max_active_runs=1,
    start_date=datetime(2023,1,1),
    schedule_interval="@weekly"
) as dag:
    task1 = PythonOperator(
        task_id="binance_top50",
        queue = "pnl_1",
        python_callable=binance_top50
    )
    task1_1 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_gl_ls10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_gl_ls10"}
    )
    task1_2 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_gl_ls11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_gl_ls11"}
    )
    task1_3 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_gl_ls12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_gl_ls12"}
    )
    task1_4 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_gl_ls13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_gl_ls13"}
    )
    task1_5 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_gl_ls8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_gl_ls8"}
    )
    task1_6 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_gl_ls9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_gl_ls9"}
    )
    task1_7 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_mom13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_mom13"}
    )
    task1_8 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_mom14",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_mom14"}
    )
    task1_9 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_mom15",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_mom15"}
    )
    task1_10 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_mom16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_mom16"}
    )
    task1_11 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_rev11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_rev11"}
    )
    task1_12 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_tp_ls3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_tp_ls3"}
    )
    task1_13 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_tp_ls4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_tp_ls4"}
    )
    task1_14 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_tp_ls5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_tp_ls5"}
    )
    task1_15 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_tp_ls6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_tp_ls6"}
    )
    task1_16 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_tp_ls7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_tp_ls7"}
    )
    task1_17 = PythonOperator(
        task_id="binance_top50_alpha_submit50_2307_alpha_tp_ls8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"alpha_submit50_2307_alpha_tp_ls8"}
    )
    task1_18 = PythonOperator(
        task_id="binance_top50_buy_volume_gap_slope_v6d_202107_ir1m2_corr7_config_buy_volume_gap_slope_20230303_031231_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_gap_slope_v6d_202107_ir1m2_corr7_config_buy_volume_gap_slope_20230303_031231_alpha_0"}
    )
    task1_19 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_0"}
    )
    task1_20 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_1"}
    )
    task1_21 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_2"}
    )
    task1_22 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202201_top100_config_buy_volume_slope_20221228_085917_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202201_top100_config_buy_volume_slope_20221228_085917_alpha_8"}
    )
    task1_23 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_1"}
    )
    task1_24 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_3"}
    )
    task1_25 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_5"}
    )
    task1_26 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_6"}
    )
    task1_27 = PythonOperator(
        task_id="binance_top50_buy_volume_slope_202205_config_buy_volume_slope_20220831_021525_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"buy_volume_slope_202205_config_buy_volume_slope_20220831_021525_alpha_3"}
    )
    task1_28 = PythonOperator(
        task_id="binance_top50_close_czn_202201_config_close_czn_20220919_084800_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_0"}
    )
    task1_29 = PythonOperator(
        task_id="binance_top50_close_czn_202201_config_close_czn_20220919_084800_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_1"}
    )
    task1_30 = PythonOperator(
        task_id="binance_top50_close_czn_202201_config_close_czn_20220919_084800_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_2"}
    )
    task1_31 = PythonOperator(
        task_id="binance_top50_close_czn_202201_config_close_czn_20220919_084800_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_4"}
    )
    task1_32 = PythonOperator(
        task_id="binance_top50_close_czn_202201_config_close_czn_20220919_084800_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_5"}
    )
    task1_33 = PythonOperator(
        task_id="binance_top50_close_czn_202203_top100_config_close_czn_20230108_161316_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202203_top100_config_close_czn_20230108_161316_alpha_5"}
    )
    task1_34 = PythonOperator(
        task_id="binance_top50_close_czn_202207_top100_config_close_czn_20230108_222715_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_202207_top100_config_close_czn_20230108_222715_alpha_3"}
    )
    task1_35 = PythonOperator(
        task_id="binance_top50_close_czn_v6c_202107_ir1m2_corr7_config_close_czn_20230221_054507_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_czn_v6c_202107_ir1m2_corr7_config_close_czn_20230221_054507_alpha_1"}
    )
    task1_36 = PythonOperator(
        task_id="binance_top50_close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_0"}
    )
    task1_37 = PythonOperator(
        task_id="binance_top50_close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_3"}
    )
    task1_38 = PythonOperator(
        task_id="binance_top50_close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_7"}
    )
    task1_39 = PythonOperator(
        task_id="binance_top50_close_level_v6d_202107_ir1m2_corr7_config_close_level_20230302_024711_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_level_v6d_202107_ir1m2_corr7_config_close_level_20230302_024711_alpha_1"}
    )
    task1_40 = PythonOperator(
        task_id="binance_top50_close_slope_202201_config_close_slope_20220831_164929_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_slope_202201_config_close_slope_20220831_164929_alpha_0"}
    )
    task1_41 = PythonOperator(
        task_id="binance_top50_close_slope_202201_config_close_slope_20220831_164929_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_slope_202201_config_close_slope_20220831_164929_alpha_2"}
    )
    task1_42 = PythonOperator(
        task_id="binance_top50_close_slope_v6c_202107_ir1m2_corr7_config_close_slope_20230218_171410_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"close_slope_v6c_202107_ir1m2_corr7_config_close_slope_20230218_171410_alpha_1"}
    )
    task1_43 = PythonOperator(
        task_id="binance_top50_corr2_level_202201_config_corr2_level_20220906_063904_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr2_level_202201_config_corr2_level_20220906_063904_alpha_1"}
    )
    task1_44 = PythonOperator(
        task_id="binance_top50_corr2_level_202205_top100_config_corr2_level_20221228_135216_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr2_level_202205_top100_config_corr2_level_20221228_135216_alpha_2"}
    )
    task1_45 = PythonOperator(
        task_id="binance_top50_corr2_level_202207_top100_config_corr2_level_20221228_172551_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr2_level_202207_top100_config_corr2_level_20221228_172551_alpha_0"}
    )
    task1_46 = PythonOperator(
        task_id="binance_top50_corr2_level_v6d_202107_ir1m2_corr7_config_corr2_level_20230306_071252_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr2_level_v6d_202107_ir1m2_corr7_config_corr2_level_20230306_071252_alpha_0"}
    )
    task1_47 = PythonOperator(
        task_id="binance_top50_corr3_level_202201_config_corr3_level_20220920_152643_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202201_config_corr3_level_20220920_152643_alpha_0"}
    )
    task1_48 = PythonOperator(
        task_id="binance_top50_corr3_level_202201_config_corr3_level_20220920_152643_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202201_config_corr3_level_20220920_152643_alpha_1"}
    )
    task1_49 = PythonOperator(
        task_id="binance_top50_corr3_level_202201_top100_config_corr3_level_20221228_044533_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202201_top100_config_corr3_level_20221228_044533_alpha_0"}
    )
    task1_50 = PythonOperator(
        task_id="binance_top50_corr3_level_202203_config_corr3_level_20220920_174101_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202203_config_corr3_level_20220920_174101_alpha_1"}
    )
    task1_51 = PythonOperator(
        task_id="binance_top50_corr3_level_202203_config_corr3_level_20220920_174101_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202203_config_corr3_level_20220920_174101_alpha_3"}
    )
    task1_52 = PythonOperator(
        task_id="binance_top50_corr3_level_202203_top100_config_corr3_level_20221228_092748_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202203_top100_config_corr3_level_20221228_092748_alpha_2"}
    )
    task1_53 = PythonOperator(
        task_id="binance_top50_corr3_level_202205_config_corr3_level_20220920_220745_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202205_config_corr3_level_20220920_220745_alpha_1"}
    )
    task1_54 = PythonOperator(
        task_id="binance_top50_corr3_level_202205_config_corr3_level_20220920_220745_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202205_config_corr3_level_20220920_220745_alpha_2"}
    )
    task1_55 = PythonOperator(
        task_id="binance_top50_corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_0"}
    )
    task1_56 = PythonOperator(
        task_id="binance_top50_corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_16"}
    )
    task1_57 = PythonOperator(
        task_id="binance_top50_corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_3"}
    )
    task1_58 = PythonOperator(
        task_id="binance_top50_corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_7"}
    )
    task1_59 = PythonOperator(
        task_id="binance_top50_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_1"}
    )
    task1_60 = PythonOperator(
        task_id="binance_top50_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_2"}
    )
    task1_61 = PythonOperator(
        task_id="binance_top50_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_40",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_40"}
    )
    task1_62 = PythonOperator(
        task_id="binance_top50_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_6"}
    )
    task1_63 = PythonOperator(
        task_id="binance_top50_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_7"}
    )
    task1_64 = PythonOperator(
        task_id="binance_top50_event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_0"}
    )
    task1_65 = PythonOperator(
        task_id="binance_top50_event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_2"}
    )
    task1_66 = PythonOperator(
        task_id="binance_top50_event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_8"}
    )
    task1_67 = PythonOperator(
        task_id="binance_top50_expr02_20220311_154351_alpha758",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"expr02_20220311_154351_alpha758"}
    )
    task1_68 = PythonOperator(
        task_id="binance_top50_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_1"}
    )
    task1_69 = PythonOperator(
        task_id="binance_top50_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_22",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_22"}
    )
    task1_70 = PythonOperator(
        task_id="binance_top50_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_3"}
    )
    task1_71 = PythonOperator(
        task_id="binance_top50_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_4"}
    )
    task1_72 = PythonOperator(
        task_id="binance_top50_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_6"}
    )
    task1_73 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls1"}
    )
    task1_74 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls2"}
    )
    task1_75 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls3"}
    )
    task1_76 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls4"}
    )
    task1_77 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls5"}
    )
    task1_78 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls6"}
    )
    task1_79 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_gl_ls7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_gl_ls7"}
    )
    task1_80 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_mom13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_mom13"}
    )
    task1_81 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_mom7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_mom7"}
    )
    task1_82 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_prem5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_prem5"}
    )
    task1_83 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_prem6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_prem6"}
    )
    task1_84 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_prem7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_prem7"}
    )
    task1_85 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_rev10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_rev10"}
    )
    task1_86 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_rev9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_rev9"}
    )
    task1_87 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_season_ls",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_season_ls"}
    )
    task1_88 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_season_ls2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_season_ls2"}
    )
    task1_89 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_season_ls3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_season_ls3"}
    )
    task1_90 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_tp_ls1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_tp_ls1"}
    )
    task1_91 = PythonOperator(
        task_id="binance_top50_hjlee_submit100_alpha_tp_ls2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_submit100_alpha_tp_ls2"}
    )
    task1_92 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_close_zscore",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_close_zscore"}
    )
    task1_93 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_fund",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_fund"}
    )
    task1_94 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_funding1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_funding1"}
    )
    task1_95 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_funding2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_funding2"}
    )
    task1_96 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_mom2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_mom2"}
    )
    task1_97 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_mom3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_mom3"}
    )
    task1_98 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_mom4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_mom4"}
    )
    task1_99 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_mom5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_mom5"}
    )
    task1_100 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_mom6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_mom6"}
    )
    task1_101 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_mom7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_mom7"}
    )
    task1_102 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_OI",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_OI"}
    )
    task1_103 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_OI2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_OI2"}
    )
    task1_104 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_OI3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_OI3"}
    )
    task1_105 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_OI4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_OI4"}
    )
    task1_106 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_OI5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_OI5"}
    )
    task1_107 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_prem",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_prem"}
    )
    task1_108 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_prem2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_prem2"}
    )
    task1_109 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_prem22",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_prem22"}
    )
    task1_110 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_premium_raw",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_premium_raw"}
    )
    task1_111 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_rev2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_rev2"}
    )
    task1_112 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_rev3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_rev3"}
    )
    task1_113 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_rev4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_rev4"}
    )
    task1_114 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_rev5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_rev5"}
    )
    task1_115 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season1_vol",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season1_vol"}
    )
    task1_116 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season1_vol_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season1_vol_2"}
    )
    task1_117 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season3"}
    )
    task1_118 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season3_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season3_2"}
    )
    task1_119 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season3_vol",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season3_vol"}
    )
    task1_120 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season_OI",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season_OI"}
    )
    task1_121 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_season_OI2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_season_OI2"}
    )
    task1_122 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_vol2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_vol2"}
    )
    task1_123 = PythonOperator(
        task_id="binance_top50_hjlee_v1_alpha_volume_p",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v1_alpha_volume_p"}
    )
    task1_124 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_liq1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_liq1"}
    )
    task1_125 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_mom10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_mom10"}
    )
    task1_126 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_mom11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_mom11"}
    )
    task1_127 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_mom12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_mom12"}
    )
    task1_128 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_mom8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_mom8"}
    )
    task1_129 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_mom9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_mom9"}
    )
    task1_130 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_OI6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_OI6"}
    )
    task1_131 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_OI7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_OI7"}
    )
    task1_132 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_OI8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_OI8"}
    )
    task1_133 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_prem5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_prem5"}
    )
    task1_134 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_prem6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_prem6"}
    )
    task1_135 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_rev1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_rev1"}
    )
    task1_136 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_rev7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_rev7"}
    )
    task1_137 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_rev8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_rev8"}
    )
    task1_138 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_season_corr",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_season_corr"}
    )
    task1_139 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_season_vol5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_season_vol5"}
    )
    task1_140 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_season_vol6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_season_vol6"}
    )
    task1_141 = PythonOperator(
        task_id="binance_top50_hjlee_v2_alpha_season_vol7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"hjlee_v2_alpha_season_vol7"}
    )
    task1_142 = PythonOperator(
        task_id="binance_top50_mom_alpha_new0_2_20220602_011900_alpha027",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"mom_alpha_new0_2_20220602_011900_alpha027"}
    )
    task1_143 = PythonOperator(
        task_id="binance_top50_premium_rev_alpha_000_20220227_223917_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"premium_rev_alpha_000_20220227_223917_alpha000"}
    )
    task1_144 = PythonOperator(
        task_id="binance_top50_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_0"}
    )
    task1_145 = PythonOperator(
        task_id="binance_top50_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_12"}
    )
    task1_146 = PythonOperator(
        task_id="binance_top50_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_2"}
    )
    task1_147 = PythonOperator(
        task_id="binance_top50_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_20",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_20"}
    )
    task1_148 = PythonOperator(
        task_id="binance_top50_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_6"}
    )
    task1_149 = PythonOperator(
        task_id="binance_top50_prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_0"}
    )
    task1_150 = PythonOperator(
        task_id="binance_top50_prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_2"}
    )
    task1_151 = PythonOperator(
        task_id="binance_top50_prem_ratio_level_202209_config_prem_ratio_level_20221216_055342_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_level_202209_config_prem_ratio_level_20221216_055342_alpha_2"}
    )
    task1_152 = PythonOperator(
        task_id="binance_top50_prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_0"}
    )
    task1_153 = PythonOperator(
        task_id="binance_top50_prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_22",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_22"}
    )
    task1_154 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_2"}
    )
    task1_155 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_3"}
    )
    task1_156 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202201_top100_config_prem_ratio_slope_20221228_005820_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202201_top100_config_prem_ratio_slope_20221228_005820_alpha_4"}
    )
    task1_157 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202203_config_prem_ratio_slope_20220920_103933_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202203_config_prem_ratio_slope_20220920_103933_alpha_1"}
    )
    task1_158 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202203_top100_config_prem_ratio_slope_20221228_065812_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202203_top100_config_prem_ratio_slope_20221228_065812_alpha_4"}
    )
    task1_159 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202205_config_prem_ratio_slope_20220920_131332_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202205_config_prem_ratio_slope_20220920_131332_alpha_0"}
    )
    task1_160 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_3"}
    )
    task1_161 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_5"}
    )
    task1_162 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_202209_top100_config_prem_ratio_slope_20221228_163728_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_202209_top100_config_prem_ratio_slope_20221228_163728_alpha_6"}
    )
    task1_163 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_12"}
    )
    task1_164 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_2"}
    )
    task1_165 = PythonOperator(
        task_id="binance_top50_prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_8"}
    )
    task1_166 = PythonOperator(
        task_id="binance_top50_prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_0"}
    )
    task1_167 = PythonOperator(
        task_id="binance_top50_prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_1"}
    )
    task1_168 = PythonOperator(
        task_id="binance_top50_prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_2"}
    )
    task1_169 = PythonOperator(
        task_id="binance_top50_prem_raw_level_202201_top100_config_prem_raw_level_20230102_042017_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_202201_top100_config_prem_raw_level_20230102_042017_alpha_3"}
    )
    task1_170 = PythonOperator(
        task_id="binance_top50_prem_raw_level_202209_config_prem_raw_level_20221216_125414_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_202209_config_prem_raw_level_20221216_125414_alpha_0"}
    )
    task1_171 = PythonOperator(
        task_id="binance_top50_prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_13"}
    )
    task1_172 = PythonOperator(
        task_id="binance_top50_prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_14",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_14"}
    )
    task1_173 = PythonOperator(
        task_id="binance_top50_prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_8"}
    )
    task1_174 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202201_config_prem_raw_slope_20220920_153502_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202201_config_prem_raw_slope_20220920_153502_alpha_0"}
    )
    task1_175 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_0"}
    )
    task1_176 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_8"}
    )
    task1_177 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_0"}
    )
    task1_178 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_1"}
    )
    task1_179 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_5"}
    )
    task1_180 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_9"}
    )
    task1_181 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202207_config_prem_raw_slope_20221218_131112_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202207_config_prem_raw_slope_20221218_131112_alpha_3"}
    )
    task1_182 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202207_top100_config_prem_raw_slope_20221228_194713_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202207_top100_config_prem_raw_slope_20221228_194713_alpha_1"}
    )
    task1_183 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_1"}
    )
    task1_184 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_4"}
    )
    task1_185 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_202209_top100_config_prem_raw_slope_20221229_002929_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_202209_top100_config_prem_raw_slope_20221229_002929_alpha_0"}
    )
    task1_186 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_0"}
    )
    task1_187 = PythonOperator(
        task_id="binance_top50_prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_5"}
    )
    task1_188 = PythonOperator(
        task_id="binance_top50_price_rev_20220314_005147_alpha4464",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"price_rev_20220314_005147_alpha4464"}
    )
    task1_189 = PythonOperator(
        task_id="binance_top50_price_rev_decay_20220225_010600_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"price_rev_decay_20220225_010600_alpha000"}
    )
    task1_190 = PythonOperator(
        task_id="binance_top50_rev_alpha_new_20220526_142427_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new_20220526_142427_alpha000"}
    )
    task1_191 = PythonOperator(
        task_id="binance_top50_rev_alpha_new2_20220526_142556_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new2_20220526_142556_alpha000"}
    )
    task1_192 = PythonOperator(
        task_id="binance_top50_rev_alpha_new3_20220526_142909_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new3_20220526_142909_alpha000"}
    )
    task1_193 = PythonOperator(
        task_id="binance_top50_rev_alpha_new4_1_20220526_143015_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new4_1_20220526_143015_alpha000"}
    )
    task1_194 = PythonOperator(
        task_id="binance_top50_rev_alpha_new7_20220527_121726_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new7_20220527_121726_alpha000"}
    )
    task1_195 = PythonOperator(
        task_id="binance_top50_rev_alpha_new8_20220526_143231_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new8_20220526_143231_alpha000"}
    )
    task1_196 = PythonOperator(
        task_id="binance_top50_rev_alpha_new9_20220526_145427_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rev_alpha_new9_20220526_145427_alpha000"}
    )
    task1_197 = PythonOperator(
        task_id="binance_top50_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_0"}
    )
    task1_198 = PythonOperator(
        task_id="binance_top50_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_11"}
    )
    task1_199 = PythonOperator(
        task_id="binance_top50_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_30",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_30"}
    )
    task1_200 = PythonOperator(
        task_id="binance_top50_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_35",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_35"}
    )
    task1_201 = PythonOperator(
        task_id="binance_top50_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_44",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_44"}
    )
    task1_202 = PythonOperator(
        task_id="binance_top50_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_8"}
    )
    task1_203 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_1"}
    )
    task1_204 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_2"}
    )
    task1_205 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_3"}
    )
    task1_206 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_4"}
    )
    task1_207 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_6"}
    )
    task1_208 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_10"}
    )
    task1_209 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_15",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_15"}
    )
    task1_210 = PythonOperator(
        task_id="binance_top50_rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_3"}
    )
    task1_211 = PythonOperator(
        task_id="binance_top50_rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_0"}
    )
    task1_212 = PythonOperator(
        task_id="binance_top50_rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_12"}
    )
    task1_213 = PythonOperator(
        task_id="binance_top50_rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_8"}
    )
    task1_214 = PythonOperator(
        task_id="binance_top50_rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_5"}
    )
    task1_215 = PythonOperator(
        task_id="binance_top50_rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_6"}
    )
    task1_216 = PythonOperator(
        task_id="binance_top50_rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_11"}
    )
    task1_217 = PythonOperator(
        task_id="binance_top50_rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_13"}
    )
    task1_218 = PythonOperator(
        task_id="binance_top50_rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_6"}
    )
    task1_219 = PythonOperator(
        task_id="binance_top50_rsi_czn_202207_config_rsi_czn_20221125_100351_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202207_config_rsi_czn_20221125_100351_alpha_11"}
    )
    task1_220 = PythonOperator(
        task_id="binance_top50_rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_5"}
    )
    task1_221 = PythonOperator(
        task_id="binance_top50_rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_7"}
    )
    task1_222 = PythonOperator(
        task_id="binance_top50_rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_11"}
    )
    task1_223 = PythonOperator(
        task_id="binance_top50_rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_7"}
    )
    task1_224 = PythonOperator(
        task_id="binance_top50_rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_1"}
    )
    task1_225 = PythonOperator(
        task_id="binance_top50_rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_7"}
    )
    task1_226 = PythonOperator(
        task_id="binance_top50_rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_8"}
    )
    task1_227 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_1"}
    )
    task1_228 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_13"}
    )
    task1_229 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_14",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_14"}
    )
    task1_230 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_16"}
    )
    task1_231 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_27",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_27"}
    )
    task1_232 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_3"}
    )
    task1_233 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_36",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_36"}
    )
    task1_234 = PythonOperator(
        task_id="binance_top50_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_50",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_50"}
    )
    task1_235 = PythonOperator(
        task_id="binance_top50_rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_0"}
    )
    task1_236 = PythonOperator(
        task_id="binance_top50_rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_1"}
    )
    task1_237 = PythonOperator(
        task_id="binance_top50_rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_3"}
    )
    task1_238 = PythonOperator(
        task_id="binance_top50_rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_6"}
    )
    task1_239 = PythonOperator(
        task_id="binance_top50_rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_1"}
    )
    task1_240 = PythonOperator(
        task_id="binance_top50_rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_3"}
    )
    task1_241 = PythonOperator(
        task_id="binance_top50_rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_0"}
    )
    task1_242 = PythonOperator(
        task_id="binance_top50_rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_2"}
    )
    task1_243 = PythonOperator(
        task_id="binance_top50_rsi_slope_202207_config_rsi_slope_20221125_040059_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"rsi_slope_202207_config_rsi_slope_20221125_040059_alpha_5"}
    )
    task1_244 = PythonOperator(
        task_id="binance_top50_seasonality2_20220311_020059_alpha3584",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"seasonality2_20220311_020059_alpha3584"}
    )
    task1_245 = PythonOperator(
        task_id="binance_top50_seasonality2_20220311_115300_alpha113",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"seasonality2_20220311_115300_alpha113"}
    )
    task1_246 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq1"}
    )
    task1_247 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq2"}
    )
    task1_248 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq3"}
    )
    task1_249 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq4"}
    )
    task1_250 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq5"}
    )
    task1_251 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq6"}
    )
    task1_252 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq7"}
    )
    task1_253 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq8"}
    )
    task1_254 = PythonOperator(
        task_id="binance_top50_submit100_alpha_liq9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_liq9"}
    )
    task1_255 = PythonOperator(
        task_id="binance_top50_submit100_alpha_mom1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_mom1"}
    )
    task1_256 = PythonOperator(
        task_id="binance_top50_submit100_alpha_mom2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_mom2"}
    )
    task1_257 = PythonOperator(
        task_id="binance_top50_submit100_alpha_mom3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_mom3"}
    )
    task1_258 = PythonOperator(
        task_id="binance_top50_submit100_alpha_mom4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_mom4"}
    )
    task1_259 = PythonOperator(
        task_id="binance_top50_submit100_alpha_mom5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_mom5"}
    )
    task1_260 = PythonOperator(
        task_id="binance_top50_submit100_alpha_mom6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_mom6"}
    )
    task1_261 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI0"}
    )
    task1_262 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI1"}
    )
    task1_263 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI10"}
    )
    task1_264 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI2"}
    )
    task1_265 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI3"}
    )
    task1_266 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI4"}
    )
    task1_267 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI5"}
    )
    task1_268 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI6"}
    )
    task1_269 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI7"}
    )
    task1_270 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI8"}
    )
    task1_271 = PythonOperator(
        task_id="binance_top50_submit100_alpha_OI9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_OI9"}
    )
    task1_272 = PythonOperator(
        task_id="binance_top50_submit100_alpha_prem1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_prem1"}
    )
    task1_273 = PythonOperator(
        task_id="binance_top50_submit100_alpha_prem2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_prem2"}
    )
    task1_274 = PythonOperator(
        task_id="binance_top50_submit100_alpha_prem3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_prem3"}
    )
    task1_275 = PythonOperator(
        task_id="binance_top50_submit100_alpha_prem4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_prem4"}
    )
    task1_276 = PythonOperator(
        task_id="binance_top50_submit100_alpha_rev2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_rev2"}
    )
    task1_277 = PythonOperator(
        task_id="binance_top50_submit100_alpha_rev3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_rev3"}
    )
    task1_278 = PythonOperator(
        task_id="binance_top50_submit100_alpha_rev4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_rev4"}
    )
    task1_279 = PythonOperator(
        task_id="binance_top50_submit100_alpha_rev5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_rev5"}
    )
    task1_280 = PythonOperator(
        task_id="binance_top50_submit100_alpha_rev6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_rev6"}
    )
    task1_281 = PythonOperator(
        task_id="binance_top50_submit100_alpha_season_1w_ret1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_season_1w_ret1"}
    )
    task1_282 = PythonOperator(
        task_id="binance_top50_submit100_alpha_season_1w_vol1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_season_1w_vol1"}
    )
    task1_283 = PythonOperator(
        task_id="binance_top50_submit100_alpha_season_OI1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_season_OI1"}
    )
    task1_284 = PythonOperator(
        task_id="binance_top50_submit100_alpha_season_vol1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_season_vol1"}
    )
    task1_285 = PythonOperator(
        task_id="binance_top50_submit100_alpha_season_vol2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_season_vol2"}
    )
    task1_286 = PythonOperator(
        task_id="binance_top50_submit100_alpha_season_vol3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_season_vol3"}
    )
    task1_287 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol1"}
    )
    task1_288 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol2"}
    )
    task1_289 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol3"}
    )
    task1_290 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol4"}
    )
    task1_291 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol5"}
    )
    task1_292 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol6"}
    )
    task1_293 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol7"}
    )
    task1_294 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol8"}
    )
    task1_295 = PythonOperator(
        task_id="binance_top50_submit100_alpha_vol9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"submit100_alpha_vol9"}
    )
    task1_296 = PythonOperator(
        task_id="binance_top50_trend5_606_decay_20220225_011129_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"trend5_606_decay_20220225_011129_alpha000"}
    )
    task1_297 = PythonOperator(
        task_id="binance_top50_ueret2_slope_202203_config_ueret2_slope_20220919_112659_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret2_slope_202203_config_ueret2_slope_20220919_112659_alpha_0"}
    )
    task1_298 = PythonOperator(
        task_id="binance_top50_ueret2_slope_202205_config_ueret2_slope_20220919_151103_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret2_slope_202205_config_ueret2_slope_20220919_151103_alpha_1"}
    )
    task1_299 = PythonOperator(
        task_id="binance_top50_ueret2_slope_202209_config_ueret2_slope_20221124_152520_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret2_slope_202209_config_ueret2_slope_20221124_152520_alpha_0"}
    )
    task1_300 = PythonOperator(
        task_id="binance_top50_ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_0"}
    )
    task1_301 = PythonOperator(
        task_id="binance_top50_ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_3"}
    )
    task1_302 = PythonOperator(
        task_id="binance_top50_ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_5"}
    )
    task1_303 = PythonOperator(
        task_id="binance_top50_ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_7"}
    )
    task1_304 = PythonOperator(
        task_id="binance_top50_ueret_slope_202201_config_ueret_slope_20220919_063901_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_slope_202201_config_ueret_slope_20220919_063901_alpha_0"}
    )
    task1_305 = PythonOperator(
        task_id="binance_top50_ueret_slope_202203_config_ueret_slope_20220919_092156_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_slope_202203_config_ueret_slope_20220919_092156_alpha_1"}
    )
    task1_306 = PythonOperator(
        task_id="binance_top50_ueret_slope_202205_config_ueret_slope_20220919_115554_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_slope_202205_config_ueret_slope_20220919_115554_alpha_2"}
    )
    task1_307 = PythonOperator(
        task_id="binance_top50_ueret_slope_202205_top100_config_ueret_slope_20221222_080247_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_slope_202205_top100_config_ueret_slope_20221222_080247_alpha_1"}
    )
    task1_308 = PythonOperator(
        task_id="binance_top50_ueret_slope_v6c_202107_ir1m2_corr7_config_ueret_slope_20230218_230855_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"ueret_slope_v6c_202107_ir1m2_corr7_config_ueret_slope_20230218_230855_alpha_2"}
    )
    task1_309 = PythonOperator(
        task_id="binance_top50_var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_12"}
    )
    task1_310 = PythonOperator(
        task_id="binance_top50_var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_7"}
    )
    task1_311 = PythonOperator(
        task_id="binance_top50_var1_slope_202201_config_var1_slope_20220830_095512_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202201_config_var1_slope_20220830_095512_alpha_0"}
    )
    task1_312 = PythonOperator(
        task_id="binance_top50_var1_slope_202201_config_var1_slope_20220830_095512_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202201_config_var1_slope_20220830_095512_alpha_1"}
    )
    task1_313 = PythonOperator(
        task_id="binance_top50_var1_slope_202201_top100_config_var1_slope_20221220_032254_alpha_16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202201_top100_config_var1_slope_20221220_032254_alpha_16"}
    )
    task1_314 = PythonOperator(
        task_id="binance_top50_var1_slope_202203_config_var1_slope_20220830_145940_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202203_config_var1_slope_20220830_145940_alpha_0"}
    )
    task1_315 = PythonOperator(
        task_id="binance_top50_var1_slope_202203_config_var1_slope_20220830_145940_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202203_config_var1_slope_20220830_145940_alpha_1"}
    )
    task1_316 = PythonOperator(
        task_id="binance_top50_var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_11"}
    )
    task1_317 = PythonOperator(
        task_id="binance_top50_var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_4"}
    )
    task1_318 = PythonOperator(
        task_id="binance_top50_var1_slope_202205_config_var1_slope_20220830_173308_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202205_config_var1_slope_20220830_173308_alpha_0"}
    )
    task1_319 = PythonOperator(
        task_id="binance_top50_var1_slope_202205_config_var1_slope_20220830_173308_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202205_config_var1_slope_20220830_173308_alpha_6"}
    )
    task1_320 = PythonOperator(
        task_id="binance_top50_var1_slope_202205_top100_config_var1_slope_20221221_044056_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202205_top100_config_var1_slope_20221221_044056_alpha_1"}
    )
    task1_321 = PythonOperator(
        task_id="binance_top50_var1_slope_202209_config_var1_slope_20221118_100742_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_202209_config_var1_slope_20221118_100742_alpha_2"}
    )
    task1_322 = PythonOperator(
        task_id="binance_top50_var1_sloperev_v6d_202107_ir1m2_corr7_config_var1_sloperev_20230302_023454_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_sloperev_v6d_202107_ir1m2_corr7_config_var1_sloperev_20230302_023454_alpha_5"}
    )
    task1_323 = PythonOperator(
        task_id="binance_top50_var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_0"}
    )
    task1_324 = PythonOperator(
        task_id="binance_top50_var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_3"}
    )
    task1_325 = PythonOperator(
        task_id="binance_top50_var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_6"}
    )
    task1_326 = PythonOperator(
        task_id="binance_top50_var2_gap_slope_v6c_202107_ir1m2_corr7_config_var2_gap_slope_20230218_221051_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_gap_slope_v6c_202107_ir1m2_corr7_config_var2_gap_slope_20230218_221051_alpha_2"}
    )
    task1_327 = PythonOperator(
        task_id="binance_top50_var2_level_202201_config_var2_level_20220902_002741_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_level_202201_config_var2_level_20220902_002741_alpha_0"}
    )
    task1_328 = PythonOperator(
        task_id="binance_top50_var2_level_202201_config_var2_level_20220902_002741_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_level_202201_config_var2_level_20220902_002741_alpha_2"}
    )
    task1_329 = PythonOperator(
        task_id="binance_top50_var2_slope_202201_config_var2_slope_20220830_095542_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_slope_202201_config_var2_slope_20220830_095542_alpha_0"}
    )
    task1_330 = PythonOperator(
        task_id="binance_top50_var2_slope_202201_config_var2_slope_20220830_095542_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_slope_202201_config_var2_slope_20220830_095542_alpha_1"}
    )
    task1_331 = PythonOperator(
        task_id="binance_top50_var2_slope_202203_config_var2_slope_20220830_132945_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_slope_202203_config_var2_slope_20220830_132945_alpha_2"}
    )
    task1_332 = PythonOperator(
        task_id="binance_top50_var2_slope_202207_top100_config_var2_slope_20221221_132625_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_slope_202207_top100_config_var2_slope_20221221_132625_alpha_0"}
    )
    task1_333 = PythonOperator(
        task_id="binance_top50_var2_slope_202209_top100_config_var2_slope_20221221_185801_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var2_slope_202209_top100_config_var2_slope_20221221_185801_alpha_0"}
    )
    task1_334 = PythonOperator(
        task_id="binance_top50_var3_slope_202201_config_var3_slope_20220831_233105_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202201_config_var3_slope_20220831_233105_alpha_0"}
    )
    task1_335 = PythonOperator(
        task_id="binance_top50_var3_slope_202201_config_var3_slope_20220831_233105_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202201_config_var3_slope_20220831_233105_alpha_2"}
    )
    task1_336 = PythonOperator(
        task_id="binance_top50_var3_slope_202203_config_var3_slope_20220901_020401_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202203_config_var3_slope_20220901_020401_alpha_1"}
    )
    task1_337 = PythonOperator(
        task_id="binance_top50_var3_slope_202203_config_var3_slope_20220901_020401_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202203_config_var3_slope_20220901_020401_alpha_3"}
    )
    task1_338 = PythonOperator(
        task_id="binance_top50_var3_slope_202205_config_var3_slope_20220901_044836_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202205_config_var3_slope_20220901_044836_alpha_0"}
    )
    task1_339 = PythonOperator(
        task_id="binance_top50_var3_slope_202205_config_var3_slope_20220901_044836_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202205_config_var3_slope_20220901_044836_alpha_5"}
    )
    task1_340 = PythonOperator(
        task_id="binance_top50_var3_slope_202207_config_var3_slope_20221121_035549_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202207_config_var3_slope_20221121_035549_alpha_3"}
    )
    task1_341 = PythonOperator(
        task_id="binance_top50_var3_slope_202207_config_var3_slope_20221121_035549_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202207_config_var3_slope_20221121_035549_alpha_5"}
    )
    task1_342 = PythonOperator(
        task_id="binance_top50_var3_slope_202207_top100_config_var3_slope_20221221_151230_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202207_top100_config_var3_slope_20221221_151230_alpha_0"}
    )
    task1_343 = PythonOperator(
        task_id="binance_top50_var3_slope_202209_config_var3_slope_20221121_094536_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202209_config_var3_slope_20221121_094536_alpha_1"}
    )
    task1_344 = PythonOperator(
        task_id="binance_top50_var3_slope_202209_config_var3_slope_20221121_094536_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"var3_slope_202209_config_var3_slope_20221121_094536_alpha_3"}
    )
    task1_345 = PythonOperator(
        task_id="binance_top50_volume_pressure_20220313_223650_alpha1094",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"volume_pressure_20220313_223650_alpha1094"}
    )
    task1_346 = PythonOperator(
        task_id="binance_top50_volume_pressure_20220313_223650_alpha2513",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top50","alpha":"volume_pressure_20220313_223650_alpha2513"}
    )
    

    task2 = PythonOperator(
        task_id="binance_top100",
        python_callable=binance_top100,
        queue = "pnl_1"
    )
    task2_1 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_gl_ls10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_gl_ls10"}
    )
    task2_2 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_gl_ls11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_gl_ls11"}
    )
    task2_3 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_gl_ls12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_gl_ls12"}
    )
    task2_4 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_gl_ls13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_gl_ls13"}
    )
    task2_5 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_gl_ls8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_gl_ls8"}
    )
    task2_6 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_gl_ls9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_gl_ls9"}
    )
    task2_7 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_mom13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_mom13"}
    )
    task2_8 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_mom14",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_mom14"}
    )
    task2_9 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_mom15",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_mom15"}
    )
    task2_10 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_mom16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_mom16"}
    )
    task2_11 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_rev11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_rev11"}
    )
    task2_12 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_tp_ls3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_tp_ls3"}
    )
    task2_13 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_tp_ls4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_tp_ls4"}
    )
    task2_14 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_tp_ls5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_tp_ls5"}
    )
    task2_15 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_tp_ls6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_tp_ls6"}
    )
    task2_16 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_tp_ls7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_tp_ls7"}
    )
    task2_17 = PythonOperator(
        task_id="binance_top100_alpha_submit50_2307_alpha_tp_ls8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"alpha_submit50_2307_alpha_tp_ls8"}
    )
    task2_18 = PythonOperator(
        task_id="binance_top100_buy_volume_gap_slope_v6d_202107_ir1m2_corr7_config_buy_volume_gap_slope_20230303_031231_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_gap_slope_v6d_202107_ir1m2_corr7_config_buy_volume_gap_slope_20230303_031231_alpha_0"}
    )
    task2_19 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_0"}
    )
    task2_20 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_1"}
    )
    task2_21 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202201_config_buy_volume_slope_20220830_163245_alpha_2"}
    )
    task2_22 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202201_top100_config_buy_volume_slope_20221228_085917_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202201_top100_config_buy_volume_slope_20221228_085917_alpha_8"}
    )
    task2_23 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_1"}
    )
    task2_24 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_3"}
    )
    task2_25 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_5"}
    )
    task2_26 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202203_config_buy_volume_slope_20220830_233858_alpha_6"}
    )
    task2_27 = PythonOperator(
        task_id="binance_top100_buy_volume_slope_202205_config_buy_volume_slope_20220831_021525_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"buy_volume_slope_202205_config_buy_volume_slope_20220831_021525_alpha_3"}
    )
    task2_28 = PythonOperator(
        task_id="binance_top100_close_czn_202201_config_close_czn_20220919_084800_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_0"}
    )
    task2_29 = PythonOperator(
        task_id="binance_top100_close_czn_202201_config_close_czn_20220919_084800_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_1"}
    )
    task2_30 = PythonOperator(
        task_id="binance_top100_close_czn_202201_config_close_czn_20220919_084800_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_2"}
    )
    task2_31 = PythonOperator(
        task_id="binance_top100_close_czn_202201_config_close_czn_20220919_084800_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_4"}
    )
    task2_32 = PythonOperator(
        task_id="binance_top100_close_czn_202201_config_close_czn_20220919_084800_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202201_config_close_czn_20220919_084800_alpha_5"}
    )
    task2_33 = PythonOperator(
        task_id="binance_top100_close_czn_202203_top100_config_close_czn_20230108_161316_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202203_top100_config_close_czn_20230108_161316_alpha_5"}
    )
    task2_34 = PythonOperator(
        task_id="binance_top100_close_czn_202207_top100_config_close_czn_20230108_222715_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_202207_top100_config_close_czn_20230108_222715_alpha_3"}
    )
    task2_35 = PythonOperator(
        task_id="binance_top100_close_czn_v6c_202107_ir1m2_corr7_config_close_czn_20230221_054507_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_czn_v6c_202107_ir1m2_corr7_config_close_czn_20230221_054507_alpha_1"}
    )
    task2_36 = PythonOperator(
        task_id="binance_top100_close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_0"}
    )
    task2_37 = PythonOperator(
        task_id="binance_top100_close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_3"}
    )
    task2_38 = PythonOperator(
        task_id="binance_top100_close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_gap_slope_v6c_202107_ir1m2_corr7_config_close_gap_slope_20230219_081038_alpha_7"}
    )
    task2_39 = PythonOperator(
        task_id="binance_top100_close_level_v6d_202107_ir1m2_corr7_config_close_level_20230302_024711_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_level_v6d_202107_ir1m2_corr7_config_close_level_20230302_024711_alpha_1"}
    )
    task2_40 = PythonOperator(
        task_id="binance_top100_close_slope_202201_config_close_slope_20220831_164929_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_slope_202201_config_close_slope_20220831_164929_alpha_0"}
    )
    task2_41 = PythonOperator(
        task_id="binance_top100_close_slope_202201_config_close_slope_20220831_164929_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_slope_202201_config_close_slope_20220831_164929_alpha_2"}
    )
    task2_42 = PythonOperator(
        task_id="binance_top100_close_slope_v6c_202107_ir1m2_corr7_config_close_slope_20230218_171410_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"close_slope_v6c_202107_ir1m2_corr7_config_close_slope_20230218_171410_alpha_1"}
    )
    task2_43 = PythonOperator(
        task_id="binance_top100_corr2_level_202201_config_corr2_level_20220906_063904_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr2_level_202201_config_corr2_level_20220906_063904_alpha_1"}
    )
    task2_44 = PythonOperator(
        task_id="binance_top100_corr2_level_202205_top100_config_corr2_level_20221228_135216_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr2_level_202205_top100_config_corr2_level_20221228_135216_alpha_2"}
    )
    task2_45 = PythonOperator(
        task_id="binance_top100_corr2_level_202207_top100_config_corr2_level_20221228_172551_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr2_level_202207_top100_config_corr2_level_20221228_172551_alpha_0"}
    )
    task2_46 = PythonOperator(
        task_id="binance_top100_corr2_level_v6d_202107_ir1m2_corr7_config_corr2_level_20230306_071252_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr2_level_v6d_202107_ir1m2_corr7_config_corr2_level_20230306_071252_alpha_0"}
    )
    task2_47 = PythonOperator(
        task_id="binance_top100_corr3_level_202201_config_corr3_level_20220920_152643_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202201_config_corr3_level_20220920_152643_alpha_0"}
    )
    task2_48 = PythonOperator(
        task_id="binance_top100_corr3_level_202201_config_corr3_level_20220920_152643_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202201_config_corr3_level_20220920_152643_alpha_1"}
    )
    task2_49 = PythonOperator(
        task_id="binance_top100_corr3_level_202201_top100_config_corr3_level_20221228_044533_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202201_top100_config_corr3_level_20221228_044533_alpha_0"}
    )
    task2_50 = PythonOperator(
        task_id="binance_top100_corr3_level_202203_config_corr3_level_20220920_174101_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202203_config_corr3_level_20220920_174101_alpha_1"}
    )
    task2_51 = PythonOperator(
        task_id="binance_top100_corr3_level_202203_config_corr3_level_20220920_174101_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202203_config_corr3_level_20220920_174101_alpha_3"}
    )
    task2_52 = PythonOperator(
        task_id="binance_top100_corr3_level_202203_top100_config_corr3_level_20221228_092748_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202203_top100_config_corr3_level_20221228_092748_alpha_2"}
    )
    task2_53 = PythonOperator(
        task_id="binance_top100_corr3_level_202205_config_corr3_level_20220920_220745_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202205_config_corr3_level_20220920_220745_alpha_1"}
    )
    task2_54 = PythonOperator(
        task_id="binance_top100_corr3_level_202205_config_corr3_level_20220920_220745_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202205_config_corr3_level_20220920_220745_alpha_2"}
    )
    task2_55 = PythonOperator(
        task_id="binance_top100_corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_0"}
    )
    task2_56 = PythonOperator(
        task_id="binance_top100_corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202205_top100_config_corr3_level_20221228_151436_alpha_16"}
    )
    task2_57 = PythonOperator(
        task_id="binance_top100_corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_3"}
    )
    task2_58 = PythonOperator(
        task_id="binance_top100_corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_202207_top100_config_corr3_level_20221228_214515_alpha_7"}
    )
    task2_59 = PythonOperator(
        task_id="binance_top100_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_1"}
    )
    task2_60 = PythonOperator(
        task_id="binance_top100_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_2"}
    )
    task2_61 = PythonOperator(
        task_id="binance_top100_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_40",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_40"}
    )
    task2_62 = PythonOperator(
        task_id="binance_top100_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_6"}
    )
    task2_63 = PythonOperator(
        task_id="binance_top100_corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"corr3_level_v6d_202107_ir1m2_corr7_config_corr3_level_20230306_144919_alpha_7"}
    )
    task2_64 = PythonOperator(
        task_id="binance_top100_event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_0"}
    )
    task2_65 = PythonOperator(
        task_id="binance_top100_event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_2"}
    )
    task2_66 = PythonOperator(
        task_id="binance_top100_event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"event_v6d_202107_allperiod_corr7_config_event_20230317_082012_alpha_8"}
    )
    task2_67 = PythonOperator(
        task_id="binance_top100_expr02_20220311_154351_alpha758",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"expr02_20220311_154351_alpha758"}
    )
    task2_68 = PythonOperator(
        task_id="binance_top100_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_1"}
    )
    task2_69 = PythonOperator(
        task_id="binance_top100_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_22",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_22"}
    )
    task2_70 = PythonOperator(
        task_id="binance_top100_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_3"}
    )
    task2_71 = PythonOperator(
        task_id="binance_top100_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_4"}
    )
    task2_72 = PythonOperator(
        task_id="binance_top100_gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"gap_event_v6d_202107_allperiod_corr7_config_gap_event_20230321_061632_alpha_6"}
    )
    task2_73 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls1"}
    )
    task2_74 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls2"}
    )
    task2_75 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls3"}
    )
    task2_76 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls4"}
    )
    task2_77 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls5"}
    )
    task2_78 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls6"}
    )
    task2_79 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_gl_ls7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_gl_ls7"}
    )
    task2_80 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_mom13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_mom13"}
    )
    task2_81 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_mom7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_mom7"}
    )
    task2_82 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_prem5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_prem5"}
    )
    task2_83 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_prem6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_prem6"}
    )
    task2_84 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_prem7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_prem7"}
    )
    task2_85 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_rev10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_rev10"}
    )
    task2_86 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_rev9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_rev9"}
    )
    task2_87 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_season_ls",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_season_ls"}
    )
    task2_88 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_season_ls2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_season_ls2"}
    )
    task2_89 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_season_ls3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_season_ls3"}
    )
    task2_90 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_tp_ls1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_tp_ls1"}
    )
    task2_91 = PythonOperator(
        task_id="binance_top100_hjlee_submit100_alpha_tp_ls2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_submit100_alpha_tp_ls2"}
    )
    task2_92 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_close_zscore",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_close_zscore"}
    )
    task2_93 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_fund",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_fund"}
    )
    task2_94 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_funding1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_funding1"}
    )
    task2_95 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_funding2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_funding2"}
    )
    task2_96 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_mom2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_mom2"}
    )
    task2_97 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_mom3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_mom3"}
    )
    task2_98 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_mom4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_mom4"}
    )
    task2_99 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_mom5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_mom5"}
    )
    task2_100 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_mom6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_mom6"}
    )
    task2_101 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_mom7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_mom7"}
    )
    task2_102 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_OI",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_OI"}
    )
    task2_103 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_OI2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_OI2"}
    )
    task2_104 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_OI3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_OI3"}
    )
    task2_105 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_OI4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_OI4"}
    )
    task2_106 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_OI5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_OI5"}
    )
    task2_107 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_prem",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_prem"}
    )
    task2_108 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_prem2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_prem2"}
    )
    task2_109 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_prem22",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_prem22"}
    )
    task2_110 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_premium_raw",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_premium_raw"}
    )
    task2_111 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_rev2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_rev2"}
    )
    task2_112 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_rev3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_rev3"}
    )
    task2_113 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_rev4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_rev4"}
    )
    task2_114 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_rev5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_rev5"}
    )
    task2_115 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season1_vol",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season1_vol"}
    )
    task2_116 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season1_vol_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season1_vol_2"}
    )
    task2_117 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season3"}
    )
    task2_118 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season3_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season3_2"}
    )
    task2_119 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season3_vol",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season3_vol"}
    )
    task2_120 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season_OI",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season_OI"}
    )
    task2_121 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_season_OI2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_season_OI2"}
    )
    task2_122 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_vol2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_vol2"}
    )
    task2_123 = PythonOperator(
        task_id="binance_top100_hjlee_v1_alpha_volume_p",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v1_alpha_volume_p"}
    )
    task2_124 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_liq1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_liq1"}
    )
    task2_125 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_mom10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_mom10"}
    )
    task2_126 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_mom11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_mom11"}
    )
    task2_127 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_mom12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_mom12"}
    )
    task2_128 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_mom8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_mom8"}
    )
    task2_129 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_mom9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_mom9"}
    )
    task2_130 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_OI6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_OI6"}
    )
    task2_131 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_OI7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_OI7"}
    )
    task2_132 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_OI8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_OI8"}
    )
    task2_133 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_prem5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_prem5"}
    )
    task2_134 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_prem6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_prem6"}
    )
    task2_135 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_rev1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_rev1"}
    )
    task2_136 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_rev7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_rev7"}
    )
    task2_137 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_rev8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_rev8"}
    )
    task2_138 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_season_corr",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_season_corr"}
    )
    task2_139 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_season_vol5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_season_vol5"}
    )
    task2_140 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_season_vol6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_season_vol6"}
    )
    task2_141 = PythonOperator(
        task_id="binance_top100_hjlee_v2_alpha_season_vol7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"hjlee_v2_alpha_season_vol7"}
    )
    task2_142 = PythonOperator(
        task_id="binance_top100_mom_alpha_new0_2_20220602_011900_alpha027",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"mom_alpha_new0_2_20220602_011900_alpha027"}
    )
    task2_143 = PythonOperator(
        task_id="binance_top100_premium_rev_alpha_000_20220227_223917_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"premium_rev_alpha_000_20220227_223917_alpha000"}
    )
    task2_144 = PythonOperator(
        task_id="binance_top100_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_0"}
    )
    task2_145 = PythonOperator(
        task_id="binance_top100_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_12"}
    )
    task2_146 = PythonOperator(
        task_id="binance_top100_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_2"}
    )
    task2_147 = PythonOperator(
        task_id="binance_top100_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_20",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_20"}
    )
    task2_148 = PythonOperator(
        task_id="binance_top100_prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_gap_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_gap_slope_20230306_231553_alpha_6"}
    )
    task2_149 = PythonOperator(
        task_id="binance_top100_prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_0"}
    )
    task2_150 = PythonOperator(
        task_id="binance_top100_prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_level_202203_config_prem_ratio_level_20221215_200355_alpha_2"}
    )
    task2_151 = PythonOperator(
        task_id="binance_top100_prem_ratio_level_202209_config_prem_ratio_level_20221216_055342_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_level_202209_config_prem_ratio_level_20221216_055342_alpha_2"}
    )
    task2_152 = PythonOperator(
        task_id="binance_top100_prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_0"}
    )
    task2_153 = PythonOperator(
        task_id="binance_top100_prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_22",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_level_v6d_202107_ir1m2_corr7_config_prem_ratio_level_20230306_071401_alpha_22"}
    )
    task2_154 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_2"}
    )
    task2_155 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202201_config_prem_ratio_slope_20220920_083356_alpha_3"}
    )
    task2_156 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202201_top100_config_prem_ratio_slope_20221228_005820_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202201_top100_config_prem_ratio_slope_20221228_005820_alpha_4"}
    )
    task2_157 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202203_config_prem_ratio_slope_20220920_103933_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202203_config_prem_ratio_slope_20220920_103933_alpha_1"}
    )
    task2_158 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202203_top100_config_prem_ratio_slope_20221228_065812_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202203_top100_config_prem_ratio_slope_20221228_065812_alpha_4"}
    )
    task2_159 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202205_config_prem_ratio_slope_20220920_131332_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202205_config_prem_ratio_slope_20220920_131332_alpha_0"}
    )
    task2_160 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_3"}
    )
    task2_161 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202205_top100_config_prem_ratio_slope_20221228_095725_alpha_5"}
    )
    task2_162 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_202209_top100_config_prem_ratio_slope_20221228_163728_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_202209_top100_config_prem_ratio_slope_20221228_163728_alpha_6"}
    )
    task2_163 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_12"}
    )
    task2_164 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_2"}
    )
    task2_165 = PythonOperator(
        task_id="binance_top100_prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_ratio_slope_v6d_202107_ir1m2_corr7_config_prem_ratio_slope_20230306_231530_alpha_8"}
    )
    task2_166 = PythonOperator(
        task_id="binance_top100_prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_0"}
    )
    task2_167 = PythonOperator(
        task_id="binance_top100_prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_1"}
    )
    task2_168 = PythonOperator(
        task_id="binance_top100_prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_202201_config_prem_raw_level_20221216_003337_alpha_2"}
    )
    task2_169 = PythonOperator(
        task_id="binance_top100_prem_raw_level_202201_top100_config_prem_raw_level_20230102_042017_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_202201_top100_config_prem_raw_level_20230102_042017_alpha_3"}
    )
    task2_170 = PythonOperator(
        task_id="binance_top100_prem_raw_level_202209_config_prem_raw_level_20221216_125414_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_202209_config_prem_raw_level_20221216_125414_alpha_0"}
    )
    task2_171 = PythonOperator(
        task_id="binance_top100_prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_13"}
    )
    task2_172 = PythonOperator(
        task_id="binance_top100_prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_14",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_14"}
    )
    task2_173 = PythonOperator(
        task_id="binance_top100_prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_level_v6d_202107_ir1m2_corr7_config_prem_raw_level_20230306_141908_alpha_8"}
    )
    task2_174 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202201_config_prem_raw_slope_20220920_153502_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202201_config_prem_raw_slope_20220920_153502_alpha_0"}
    )
    task2_175 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_0"}
    )
    task2_176 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202201_top100_config_prem_raw_slope_20221228_063524_alpha_8"}
    )
    task2_177 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_0"}
    )
    task2_178 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202203_config_prem_raw_slope_20220920_171737_alpha_1"}
    )
    task2_179 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_5"}
    )
    task2_180 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202203_top100_config_prem_raw_slope_20221228_110310_alpha_9"}
    )
    task2_181 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202207_config_prem_raw_slope_20221218_131112_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202207_config_prem_raw_slope_20221218_131112_alpha_3"}
    )
    task2_182 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202207_top100_config_prem_raw_slope_20221228_194713_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202207_top100_config_prem_raw_slope_20221228_194713_alpha_1"}
    )
    task2_183 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_1"}
    )
    task2_184 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202209_config_prem_raw_slope_20221219_032003_alpha_4"}
    )
    task2_185 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_202209_top100_config_prem_raw_slope_20221229_002929_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_202209_top100_config_prem_raw_slope_20221229_002929_alpha_0"}
    )
    task2_186 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_0"}
    )
    task2_187 = PythonOperator(
        task_id="binance_top100_prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"prem_raw_slope_v6d_202107_ir1m2_corr7_config_prem_raw_slope_20230307_081929_alpha_5"}
    )
    task2_188 = PythonOperator(
        task_id="binance_top100_price_rev_20220314_005147_alpha4464",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"price_rev_20220314_005147_alpha4464"}
    )
    task2_189 = PythonOperator(
        task_id="binance_top100_price_rev_decay_20220225_010600_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"price_rev_decay_20220225_010600_alpha000"}
    )
    task2_190 = PythonOperator(
        task_id="binance_top100_rev_alpha_new_20220526_142427_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new_20220526_142427_alpha000"}
    )
    task2_191 = PythonOperator(
        task_id="binance_top100_rev_alpha_new2_20220526_142556_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new2_20220526_142556_alpha000"}
    )
    task2_192 = PythonOperator(
        task_id="binance_top100_rev_alpha_new3_20220526_142909_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new3_20220526_142909_alpha000"}
    )
    task2_193 = PythonOperator(
        task_id="binance_top100_rev_alpha_new4_1_20220526_143015_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new4_1_20220526_143015_alpha000"}
    )
    task2_194 = PythonOperator(
        task_id="binance_top100_rev_alpha_new7_20220527_121726_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new7_20220527_121726_alpha000"}
    )
    task2_195 = PythonOperator(
        task_id="binance_top100_rev_alpha_new8_20220526_143231_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new8_20220526_143231_alpha000"}
    )
    task2_196 = PythonOperator(
        task_id="binance_top100_rev_alpha_new9_20220526_145427_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rev_alpha_new9_20220526_145427_alpha000"}
    )
    task2_197 = PythonOperator(
        task_id="binance_top100_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_0"}
    )
    task2_198 = PythonOperator(
        task_id="binance_top100_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_11"}
    )
    task2_199 = PythonOperator(
        task_id="binance_top100_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_30",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_30"}
    )
    task2_200 = PythonOperator(
        task_id="binance_top100_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_35",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_35"}
    )
    task2_201 = PythonOperator(
        task_id="binance_top100_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_44",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_44"}
    )
    task2_202 = PythonOperator(
        task_id="binance_top100_rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi2_czn_v6c_202107_ir1m2_corr7_config_rsi2_czn_20230222_011052_alpha_8"}
    )
    task2_203 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_1"}
    )
    task2_204 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_2"}
    )
    task2_205 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_3"}
    )
    task2_206 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_4"}
    )
    task2_207 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_config_rsi_czn_20220918_154151_alpha_6"}
    )
    task2_208 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_10"}
    )
    task2_209 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_15",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_15"}
    )
    task2_210 = PythonOperator(
        task_id="binance_top100_rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202201_top100_config_rsi_czn_20230108_114629_alpha_3"}
    )
    task2_211 = PythonOperator(
        task_id="binance_top100_rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_0"}
    )
    task2_212 = PythonOperator(
        task_id="binance_top100_rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_12"}
    )
    task2_213 = PythonOperator(
        task_id="binance_top100_rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202203_top100_config_rsi_czn_20230108_142716_alpha_8"}
    )
    task2_214 = PythonOperator(
        task_id="binance_top100_rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_5"}
    )
    task2_215 = PythonOperator(
        task_id="binance_top100_rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202205_config_rsi_czn_20220918_224612_alpha_6"}
    )
    task2_216 = PythonOperator(
        task_id="binance_top100_rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_11"}
    )
    task2_217 = PythonOperator(
        task_id="binance_top100_rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_13"}
    )
    task2_218 = PythonOperator(
        task_id="binance_top100_rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202205_top100_config_rsi_czn_20230108_163532_alpha_6"}
    )
    task2_219 = PythonOperator(
        task_id="binance_top100_rsi_czn_202207_config_rsi_czn_20221125_100351_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202207_config_rsi_czn_20221125_100351_alpha_11"}
    )
    task2_220 = PythonOperator(
        task_id="binance_top100_rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_5"}
    )
    task2_221 = PythonOperator(
        task_id="binance_top100_rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202207_top100_config_rsi_czn_20230108_192226_alpha_7"}
    )
    task2_222 = PythonOperator(
        task_id="binance_top100_rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_11"}
    )
    task2_223 = PythonOperator(
        task_id="binance_top100_rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202209_config_rsi_czn_20221125_171446_alpha_7"}
    )
    task2_224 = PythonOperator(
        task_id="binance_top100_rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_1"}
    )
    task2_225 = PythonOperator(
        task_id="binance_top100_rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_7"}
    )
    task2_226 = PythonOperator(
        task_id="binance_top100_rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_202209_top100_config_rsi_czn_20230108_214230_alpha_8"}
    )
    task2_227 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_1"}
    )
    task2_228 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_13",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_13"}
    )
    task2_229 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_14",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_14"}
    )
    task2_230 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_16"}
    )
    task2_231 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_27",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_27"}
    )
    task2_232 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_3"}
    )
    task2_233 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_36",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_36"}
    )
    task2_234 = PythonOperator(
        task_id="binance_top100_rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_50",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_czn_v6c_202107_ir1m2_corr7_config_rsi_czn_20230221_060325_alpha_50"}
    )
    task2_235 = PythonOperator(
        task_id="binance_top100_rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_0"}
    )
    task2_236 = PythonOperator(
        task_id="binance_top100_rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202201_config_rsi_slope_20220831_164848_alpha_1"}
    )
    task2_237 = PythonOperator(
        task_id="binance_top100_rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_3"}
    )
    task2_238 = PythonOperator(
        task_id="binance_top100_rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202201_top100_config_rsi_slope_20221222_001141_alpha_6"}
    )
    task2_239 = PythonOperator(
        task_id="binance_top100_rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_1"}
    )
    task2_240 = PythonOperator(
        task_id="binance_top100_rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202203_config_rsi_slope_20220831_203312_alpha_3"}
    )
    task2_241 = PythonOperator(
        task_id="binance_top100_rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_0"}
    )
    task2_242 = PythonOperator(
        task_id="binance_top100_rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202203_top100_config_rsi_slope_20221222_042146_alpha_2"}
    )
    task2_243 = PythonOperator(
        task_id="binance_top100_rsi_slope_202207_config_rsi_slope_20221125_040059_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"rsi_slope_202207_config_rsi_slope_20221125_040059_alpha_5"}
    )
    task2_244 = PythonOperator(
        task_id="binance_top100_seasonality2_20220311_020059_alpha3584",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"seasonality2_20220311_020059_alpha3584"}
    )
    task2_245 = PythonOperator(
        task_id="binance_top100_seasonality2_20220311_115300_alpha113",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"seasonality2_20220311_115300_alpha113"}
    )
    task2_246 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq1"}
    )
    task2_247 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq2"}
    )
    task2_248 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq3"}
    )
    task2_249 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq4"}
    )
    task2_250 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq5"}
    )
    task2_251 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq6"}
    )
    task2_252 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq7"}
    )
    task2_253 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq8"}
    )
    task2_254 = PythonOperator(
        task_id="binance_top100_submit100_alpha_liq9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_liq9"}
    )
    task2_255 = PythonOperator(
        task_id="binance_top100_submit100_alpha_mom1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_mom1"}
    )
    task2_256 = PythonOperator(
        task_id="binance_top100_submit100_alpha_mom2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_mom2"}
    )
    task2_257 = PythonOperator(
        task_id="binance_top100_submit100_alpha_mom3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_mom3"}
    )
    task2_258 = PythonOperator(
        task_id="binance_top100_submit100_alpha_mom4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_mom4"}
    )
    task2_259 = PythonOperator(
        task_id="binance_top100_submit100_alpha_mom5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_mom5"}
    )
    task2_260 = PythonOperator(
        task_id="binance_top100_submit100_alpha_mom6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_mom6"}
    )
    task2_261 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI0"}
    )
    task2_262 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI1"}
    )
    task2_263 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI10",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI10"}
    )
    task2_264 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI2"}
    )
    task2_265 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI3"}
    )
    task2_266 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI4"}
    )
    task2_267 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI5"}
    )
    task2_268 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI6"}
    )
    task2_269 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI7"}
    )
    task2_270 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI8"}
    )
    task2_271 = PythonOperator(
        task_id="binance_top100_submit100_alpha_OI9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_OI9"}
    )
    task2_272 = PythonOperator(
        task_id="binance_top100_submit100_alpha_prem1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_prem1"}
    )
    task2_273 = PythonOperator(
        task_id="binance_top100_submit100_alpha_prem2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_prem2"}
    )
    task2_274 = PythonOperator(
        task_id="binance_top100_submit100_alpha_prem3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_prem3"}
    )
    task2_275 = PythonOperator(
        task_id="binance_top100_submit100_alpha_prem4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_prem4"}
    )
    task2_276 = PythonOperator(
        task_id="binance_top100_submit100_alpha_rev2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_rev2"}
    )
    task2_277 = PythonOperator(
        task_id="binance_top100_submit100_alpha_rev3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_rev3"}
    )
    task2_278 = PythonOperator(
        task_id="binance_top100_submit100_alpha_rev4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_rev4"}
    )
    task2_279 = PythonOperator(
        task_id="binance_top100_submit100_alpha_rev5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_rev5"}
    )
    task2_280 = PythonOperator(
        task_id="binance_top100_submit100_alpha_rev6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_rev6"}
    )
    task2_281 = PythonOperator(
        task_id="binance_top100_submit100_alpha_season_1w_ret1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_season_1w_ret1"}
    )
    task2_282 = PythonOperator(
        task_id="binance_top100_submit100_alpha_season_1w_vol1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_season_1w_vol1"}
    )
    task2_283 = PythonOperator(
        task_id="binance_top100_submit100_alpha_season_OI1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_season_OI1"}
    )
    task2_284 = PythonOperator(
        task_id="binance_top100_submit100_alpha_season_vol1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_season_vol1"}
    )
    task2_285 = PythonOperator(
        task_id="binance_top100_submit100_alpha_season_vol2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_season_vol2"}
    )
    task2_286 = PythonOperator(
        task_id="binance_top100_submit100_alpha_season_vol3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_season_vol3"}
    )
    task2_287 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol1"}
    )
    task2_288 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol2"}
    )
    task2_289 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol3"}
    )
    task2_290 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol4"}
    )
    task2_291 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol5"}
    )
    task2_292 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol6"}
    )
    task2_293 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol7"}
    )
    task2_294 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol8",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol8"}
    )
    task2_295 = PythonOperator(
        task_id="binance_top100_submit100_alpha_vol9",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"submit100_alpha_vol9"}
    )
    task2_296 = PythonOperator(
        task_id="binance_top100_trend5_606_decay_20220225_011129_alpha000",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"trend5_606_decay_20220225_011129_alpha000"}
    )
    task2_297 = PythonOperator(
        task_id="binance_top100_ueret2_slope_202203_config_ueret2_slope_20220919_112659_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret2_slope_202203_config_ueret2_slope_20220919_112659_alpha_0"}
    )
    task2_298 = PythonOperator(
        task_id="binance_top100_ueret2_slope_202205_config_ueret2_slope_20220919_151103_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret2_slope_202205_config_ueret2_slope_20220919_151103_alpha_1"}
    )
    task2_299 = PythonOperator(
        task_id="binance_top100_ueret2_slope_202209_config_ueret2_slope_20221124_152520_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret2_slope_202209_config_ueret2_slope_20221124_152520_alpha_0"}
    )
    task2_300 = PythonOperator(
        task_id="binance_top100_ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_0"}
    )
    task2_301 = PythonOperator(
        task_id="binance_top100_ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret2_slope_v6c_202107_ir1m2_corr7_config_ueret2_slope_20230221_011342_alpha_3"}
    )
    task2_302 = PythonOperator(
        task_id="binance_top100_ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_5"}
    )
    task2_303 = PythonOperator(
        task_id="binance_top100_ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_gap_slope_v6c_202107_ir1m2_corr7_config_ueret_gap_slope_20230221_090229_alpha_7"}
    )
    task2_304 = PythonOperator(
        task_id="binance_top100_ueret_slope_202201_config_ueret_slope_20220919_063901_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_slope_202201_config_ueret_slope_20220919_063901_alpha_0"}
    )
    task2_305 = PythonOperator(
        task_id="binance_top100_ueret_slope_202203_config_ueret_slope_20220919_092156_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_slope_202203_config_ueret_slope_20220919_092156_alpha_1"}
    )
    task2_306 = PythonOperator(
        task_id="binance_top100_ueret_slope_202205_config_ueret_slope_20220919_115554_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_slope_202205_config_ueret_slope_20220919_115554_alpha_2"}
    )
    task2_307 = PythonOperator(
        task_id="binance_top100_ueret_slope_202205_top100_config_ueret_slope_20221222_080247_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_slope_202205_top100_config_ueret_slope_20221222_080247_alpha_1"}
    )
    task2_308 = PythonOperator(
        task_id="binance_top100_ueret_slope_v6c_202107_ir1m2_corr7_config_ueret_slope_20230218_230855_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"ueret_slope_v6c_202107_ir1m2_corr7_config_ueret_slope_20230218_230855_alpha_2"}
    )
    task2_309 = PythonOperator(
        task_id="binance_top100_var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_12",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_12"}
    )
    task2_310 = PythonOperator(
        task_id="binance_top100_var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_7",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_gap_slope_v6c_202107_ir1m2_corr7_config_var1_gap_slope_20230218_172742_alpha_7"}
    )
    task2_311 = PythonOperator(
        task_id="binance_top100_var1_slope_202201_config_var1_slope_20220830_095512_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202201_config_var1_slope_20220830_095512_alpha_0"}
    )
    task2_312 = PythonOperator(
        task_id="binance_top100_var1_slope_202201_config_var1_slope_20220830_095512_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202201_config_var1_slope_20220830_095512_alpha_1"}
    )
    task2_313 = PythonOperator(
        task_id="binance_top100_var1_slope_202201_top100_config_var1_slope_20221220_032254_alpha_16",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202201_top100_config_var1_slope_20221220_032254_alpha_16"}
    )
    task2_314 = PythonOperator(
        task_id="binance_top100_var1_slope_202203_config_var1_slope_20220830_145940_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202203_config_var1_slope_20220830_145940_alpha_0"}
    )
    task2_315 = PythonOperator(
        task_id="binance_top100_var1_slope_202203_config_var1_slope_20220830_145940_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202203_config_var1_slope_20220830_145940_alpha_1"}
    )
    task2_316 = PythonOperator(
        task_id="binance_top100_var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_11",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_11"}
    )
    task2_317 = PythonOperator(
        task_id="binance_top100_var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_4",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202203_top100_config_var1_slope_20221221_010023_alpha_4"}
    )
    task2_318 = PythonOperator(
        task_id="binance_top100_var1_slope_202205_config_var1_slope_20220830_173308_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202205_config_var1_slope_20220830_173308_alpha_0"}
    )
    task2_319 = PythonOperator(
        task_id="binance_top100_var1_slope_202205_config_var1_slope_20220830_173308_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202205_config_var1_slope_20220830_173308_alpha_6"}
    )
    task2_320 = PythonOperator(
        task_id="binance_top100_var1_slope_202205_top100_config_var1_slope_20221221_044056_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202205_top100_config_var1_slope_20221221_044056_alpha_1"}
    )
    task2_321 = PythonOperator(
        task_id="binance_top100_var1_slope_202209_config_var1_slope_20221118_100742_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_202209_config_var1_slope_20221118_100742_alpha_2"}
    )
    task2_322 = PythonOperator(
        task_id="binance_top100_var1_sloperev_v6d_202107_ir1m2_corr7_config_var1_sloperev_20230302_023454_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_sloperev_v6d_202107_ir1m2_corr7_config_var1_sloperev_20230302_023454_alpha_5"}
    )
    task2_323 = PythonOperator(
        task_id="binance_top100_var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_0"}
    )
    task2_324 = PythonOperator(
        task_id="binance_top100_var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_3"}
    )
    task2_325 = PythonOperator(
        task_id="binance_top100_var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_6",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var1_slope_v6c_202107_ir1m2_corr7_config_var1_slope_20230218_171303_alpha_6"}
    )
    task2_326 = PythonOperator(
        task_id="binance_top100_var2_gap_slope_v6c_202107_ir1m2_corr7_config_var2_gap_slope_20230218_221051_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_gap_slope_v6c_202107_ir1m2_corr7_config_var2_gap_slope_20230218_221051_alpha_2"}
    )
    task2_327 = PythonOperator(
        task_id="binance_top100_var2_level_202201_config_var2_level_20220902_002741_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_level_202201_config_var2_level_20220902_002741_alpha_0"}
    )
    task2_328 = PythonOperator(
        task_id="binance_top100_var2_level_202201_config_var2_level_20220902_002741_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_level_202201_config_var2_level_20220902_002741_alpha_2"}
    )
    task2_329 = PythonOperator(
        task_id="binance_top100_var2_slope_202201_config_var2_slope_20220830_095542_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_slope_202201_config_var2_slope_20220830_095542_alpha_0"}
    )
    task2_330 = PythonOperator(
        task_id="binance_top100_var2_slope_202201_config_var2_slope_20220830_095542_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_slope_202201_config_var2_slope_20220830_095542_alpha_1"}
    )
    task2_331 = PythonOperator(
        task_id="binance_top100_var2_slope_202203_config_var2_slope_20220830_132945_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_slope_202203_config_var2_slope_20220830_132945_alpha_2"}
    )
    task2_332 = PythonOperator(
        task_id="binance_top100_var2_slope_202207_top100_config_var2_slope_20221221_132625_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_slope_202207_top100_config_var2_slope_20221221_132625_alpha_0"}
    )
    task2_333 = PythonOperator(
        task_id="binance_top100_var2_slope_202209_top100_config_var2_slope_20221221_185801_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var2_slope_202209_top100_config_var2_slope_20221221_185801_alpha_0"}
    )
    task2_334 = PythonOperator(
        task_id="binance_top100_var3_slope_202201_config_var3_slope_20220831_233105_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202201_config_var3_slope_20220831_233105_alpha_0"}
    )
    task2_335 = PythonOperator(
        task_id="binance_top100_var3_slope_202201_config_var3_slope_20220831_233105_alpha_2",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202201_config_var3_slope_20220831_233105_alpha_2"}
    )
    task2_336 = PythonOperator(
        task_id="binance_top100_var3_slope_202203_config_var3_slope_20220901_020401_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202203_config_var3_slope_20220901_020401_alpha_1"}
    )
    task2_337 = PythonOperator(
        task_id="binance_top100_var3_slope_202203_config_var3_slope_20220901_020401_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202203_config_var3_slope_20220901_020401_alpha_3"}
    )
    task2_338 = PythonOperator(
        task_id="binance_top100_var3_slope_202205_config_var3_slope_20220901_044836_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202205_config_var3_slope_20220901_044836_alpha_0"}
    )
    task2_339 = PythonOperator(
        task_id="binance_top100_var3_slope_202205_config_var3_slope_20220901_044836_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202205_config_var3_slope_20220901_044836_alpha_5"}
    )
    task2_340 = PythonOperator(
        task_id="binance_top100_var3_slope_202207_config_var3_slope_20221121_035549_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202207_config_var3_slope_20221121_035549_alpha_3"}
    )
    task2_341 = PythonOperator(
        task_id="binance_top100_var3_slope_202207_config_var3_slope_20221121_035549_alpha_5",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202207_config_var3_slope_20221121_035549_alpha_5"}
    )
    task2_342 = PythonOperator(
        task_id="binance_top100_var3_slope_202207_top100_config_var3_slope_20221221_151230_alpha_0",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202207_top100_config_var3_slope_20221221_151230_alpha_0"}
    )
    task2_343 = PythonOperator(
        task_id="binance_top100_var3_slope_202209_config_var3_slope_20221121_094536_alpha_1",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202209_config_var3_slope_20221121_094536_alpha_1"}
    )
    task2_344 = PythonOperator(
        task_id="binance_top100_var3_slope_202209_config_var3_slope_20221121_094536_alpha_3",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"var3_slope_202209_config_var3_slope_20221121_094536_alpha_3"}
    )
    task2_345 = PythonOperator(
        task_id="binance_top100_volume_pressure_20220313_223650_alpha1094",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"volume_pressure_20220313_223650_alpha1094"}
    )
    task2_346 = PythonOperator(
        task_id="binance_top100_volume_pressure_20220313_223650_alpha2513",
        python_callable=pnl_generation,
        queue = "pnl_1",
        op_kwargs={"name":"binance_top100","alpha":"volume_pressure_20220313_223650_alpha2513"}
    )



task1 >> [task1_1,task1_2,task1_3,task1_4,task1_5,task1_6,task1_7,task1_8,task1_9,task1_10,task1_11,task1_12,task1_13,task1_14,task1_15,task1_16,task1_17,task1_18,task1_19,task1_20,
task1_21,task1_22,task1_23,task1_24,task1_25,task1_26,task1_27,task1_28,task1_29,task1_30,task1_31,task1_32,task1_33,task1_34,task1_35,task1_36,task1_37,task1_38,task1_39,task1_40,
task1_41,task1_42,task1_43,task1_44,task1_45,task1_46,task1_47,task1_48,task1_49,task1_50,task1_51,task1_52,task1_53,task1_54,task1_55,task1_56,task1_57,task1_58,task1_59,task1_60,
task1_61,task1_62,task1_63,task1_64,task1_65,task1_66,task1_67,task1_68,task1_69,task1_70,task1_71,task1_72,task1_73,task1_74,task1_75,task1_76,task1_77,task1_78,task1_79,task1_80,
task1_81,task1_82,task1_83,task1_84,task1_85,task1_86,task1_87,task1_88,task1_89,task1_90,task1_91,task1_92,task1_93,task1_94,task1_95,task1_96,task1_97,task1_98,task1_99,task1_100,
task1_101,task1_102,task1_103,task1_104,task1_105,task1_106,task1_107,task1_108,task1_109,task1_110,task1_111,task1_112,task1_113,task1_114,task1_115,task1_116,task1_117,task1_118,task1_119,task1_120,
task1_121,task1_122,task1_123,task1_124,task1_125,task1_126,task1_127,task1_128,task1_129,task1_130,task1_131,task1_132,task1_133,task1_134,task1_135,task1_136,task1_137,task1_138,task1_139,task1_140,
task1_141,task1_142,task1_143,task1_144,task1_145,task1_146,task1_147,task1_148,task1_149,task1_150,task1_151,task1_152,task1_153,task1_154,task1_155,task1_156,task1_157,task1_158,task1_159,task1_160,
task1_161,task1_162,task1_163,task1_164,task1_165,task1_166,task1_167,task1_168,task1_169,task1_170,task1_171,task1_172,task1_173,task1_174,task1_175,task1_176,task1_177,task1_178,task1_179,task1_180,
task1_181,task1_182,task1_183,task1_184,task1_185,task1_186,task1_187,task1_188,task1_189,task1_190,task1_191,task1_192,task1_193,task1_194,task1_195,task1_196,task1_197,task1_198,task1_199,task1_200,
task1_201,task1_202,task1_203,task1_204,task1_205,task1_206,task1_207,task1_208,task1_209,task1_210,task1_211,task1_212,task1_213,task1_214,task1_215,task1_216,task1_217,task1_218,task1_219,task1_220,
task1_221,task1_222,task1_223,task1_224,task1_225,task1_226,task1_227,task1_228,task1_229,task1_230,task1_231,task1_232,task1_233,task1_234,task1_235,task1_236,task1_237,task1_238,task1_239,task1_240,
task1_241,task1_242,task1_243,task1_244,task1_245,task1_246,task1_247,task1_248,task1_249,task1_250,task1_251,task1_252,task1_253,task1_254,task1_255,task1_256,task1_257,task1_258,task1_259,task1_260,
task1_261,task1_262,task1_263,task1_264,task1_265,task1_266,task1_267,task1_268,task1_269,task1_270,task1_271,task1_272,task1_273,task1_274,task1_275,task1_276,task1_277,task1_278,task1_279,task1_280,
task1_281,task1_282,task1_283,task1_284,task1_285,task1_286,task1_287,task1_288,task1_289,task1_290,task1_291,task1_292,task1_293,task1_294,task1_295,task1_296,task1_297,task1_298,task1_299,task1_300,
task1_301,task1_302,task1_303,task1_304,task1_305,task1_306,task1_307,task1_308,task1_309,task1_310,task1_311,task1_312,task1_313,task1_314,task1_315,task1_316,task1_317,task1_318,task1_319,task1_320,
task1_321,task1_322,task1_323,task1_324,task1_325,task1_326,task1_327,task1_328,task1_329,task1_330,task1_331,task1_332,task1_333,task1_334,task1_335,task1_336,task1_337,task1_338,task1_339,task1_340,
task1_341,task1_342,task1_343,task1_344,task1_345,task1_346]
    
task2 >> [task2_1,task2_2,task2_3,task2_4,task2_5,task2_6,task2_7,task2_8,task2_9,task2_10,task2_11,task2_12,task2_13,task2_14,task2_15,task2_16,task2_17,task2_18,task2_19,task2_20,
task2_21,task2_22,task2_23,task2_24,task2_25,task2_26,task2_27,task2_28,task2_29,task2_30,task2_31,task2_32,task2_33,task2_34,task2_35,task2_36,task2_37,task2_38,task2_39,task2_40,
task2_41,task2_42,task2_43,task2_44,task2_45,task2_46,task2_47,task2_48,task2_49,task2_50,task2_51,task2_52,task2_53,task2_54,task2_55,task2_56,task2_57,task2_58,task2_59,task2_60,
task2_61,task2_62,task2_63,task2_64,task2_65,task2_66,task2_67,task2_68,task2_69,task2_70,task2_71,task2_72,task2_73,task2_74,task2_75,task2_76,task2_77,task2_78,task2_79,task2_80,
task2_81,task2_82,task2_83,task2_84,task2_85,task2_86,task2_87,task2_88,task2_89,task2_90,task2_91,task2_92,task2_93,task2_94,task2_95,task2_96,task2_97,task2_98,task2_99,task2_100,
task2_101,task2_102,task2_103,task2_104,task2_105,task2_106,task2_107,task2_108,task2_109,task2_110,task2_111,task2_112,task2_113,task2_114,task2_115,task2_116,task2_117,task2_118,task2_119,task2_120,
task2_121,task2_122,task2_123,task2_124,task2_125,task2_126,task2_127,task2_128,task2_129,task2_130,task2_131,task2_132,task2_133,task2_134,task2_135,task2_136,task2_137,task2_138,task2_139,task2_140,
task2_141,task2_142,task2_143,task2_144,task2_145,task2_146,task2_147,task2_148,task2_149,task2_150,task2_151,task2_152,task2_153,task2_154,task2_155,task2_156,task2_157,task2_158,task2_159,task2_160,
task2_161,task2_162,task2_163,task2_164,task2_165,task2_166,task2_167,task2_168,task2_169,task2_170,task2_171,task2_172,task2_173,task2_174,task2_175,task2_176,task2_177,task2_178,task2_179,task2_180,
task2_181,task2_182,task2_183,task2_184,task2_185,task2_186,task2_187,task2_188,task2_189,task2_190,task2_191,task2_192,task2_193,task2_194,task2_195,task2_196,task2_197,task2_198,task2_199,task2_200,
task2_201,task2_202,task2_203,task2_204,task2_205,task2_206,task2_207,task2_208,task2_209,task2_210,task2_211,task2_212,task2_213,task2_214,task2_215,task2_216,task2_217,task2_218,task2_219,task2_220,
task2_221,task2_222,task2_223,task2_224,task2_225,task2_226,task2_227,task2_228,task2_229,task2_230,task2_231,task2_232,task2_233,task2_234,task2_235,task2_236,task2_237,task2_238,task2_239,task2_240,
task2_241,task2_242,task2_243,task2_244,task2_245,task2_246,task2_247,task2_248,task2_249,task2_250,task2_251,task2_252,task2_253,task2_254,task2_255,task2_256,task2_257,task2_258,task2_259,task2_260,
task2_261,task2_262,task2_263,task2_264,task2_265,task2_266,task2_267,task2_268,task2_269,task2_270,task2_271,task2_272,task2_273,task2_274,task2_275,task2_276,task2_277,task2_278,task2_279,task2_280,
task2_281,task2_282,task2_283,task2_284,task2_285,task2_286,task2_287,task2_288,task2_289,task2_290,task2_291,task2_292,task2_293,task2_294,task2_295,task2_296,task2_297,task2_298,task2_299,task2_300,
task2_301,task2_302,task2_303,task2_304,task2_305,task2_306,task2_307,task2_308,task2_309,task2_310,task2_311,task2_312,task2_313,task2_314,task2_315,task2_316,task2_317,task2_318,task2_319,task2_320,
task2_321,task2_322,task2_323,task2_324,task2_325,task2_326,task2_327,task2_328,task2_329,task2_330,task2_331,task2_332,task2_333,task2_334,task2_335,task2_336,task2_337,task2_338,task2_339,task2_340,
task2_341,task2_342,task2_343,task2_344,task2_345,task2_346]
