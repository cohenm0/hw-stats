import subprocess
from multiprocessing import Process
from time import sleep

import psutil
from sqlalchemy.orm import Session

from hwstats.backend import get_cpu_percents_for_pidHash, get_db_connection
from hwstats.monitor import start_metrics_collection


def test_cpu_load(db_path: str) -> None:
    """System test to confimr that we can properly collect CPU load for a process"""
    INTERVAL_SECONDS = 1.0
    TIMEOUT_SECONDS = 30.0
    TEST_CPU_LOAD = 53

    # Start the metrics collection process
    metrics_process = Process(
        target=start_metrics_collection,
        args=[INTERVAL_SECONDS],
        kwargs={"timeout": TIMEOUT_SECONDS, "db_path": db_path},
    )
    metrics_process.start()

    # Start workload. This calls stress-ng, which starts a child process to load one CPU at 53%
    stress_cmd = ["stress-ng", "--cpu", "1", "--cpu-load", f"{TEST_CPU_LOAD}", "--timeout", "30s"]
    with subprocess.Popen(stress_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as stress:
        # stress = subprocess.Popen(stress_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f"Process pid is {stress.pid}")
        stress_process = psutil.Process(stress.pid)

        # We need to wait for stress-ng to start it's child processes
        sleep(5)
        child_process = stress_process.children()[0]
        stress_child_hash = hash(child_process)
        print(stress.stdout.read().decode("utf-8"))

    # Wait for metrics collection to finish
    metrics_process.join()

    # Connect to the database and query for the CPU load
    engine = get_db_connection(db_path)
    session = Session(engine)

    print(f"Stress_child_hash: {stress_child_hash}")
    stress_cpu_percents = get_cpu_percents_for_pidHash(stress_child_hash, session)
    assert len(stress_cpu_percents) > 0
    avg_stress = sum(stress_cpu_percents) / len(stress_cpu_percents)

    # Test that the average CPU load is within 10% of the expected load
    assert avg_stress > (TEST_CPU_LOAD * 0.9)
    assert avg_stress < (TEST_CPU_LOAD * 1.1)
