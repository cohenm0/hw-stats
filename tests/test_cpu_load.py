import logging
import os
import subprocess
from multiprocessing import Process
from time import sleep

import psutil
from sqlalchemy.orm import Session

from hwstats import COLLECTION_INTERVAL_SECONDS, models
from hwstats.backend import get_cpu_percents_for_pidHash, get_db_connection
from hwstats.monitor import hash_process, start_metrics_collection

logger = logging.getLogger(__name__)


def test_cpu_load(db_path: str) -> None:
    """System test to confimr that we can properly collect CPU load for a process"""
    TIMEOUT_SECONDS = 30.0
    TEST_CPU_LOAD = 53

    # Start the metrics collection process
    metrics_process = Process(
        target=start_metrics_collection,
        args=[COLLECTION_INTERVAL_SECONDS],
        kwargs={"timeout": TIMEOUT_SECONDS, "db_path": db_path},
    )
    print("Starting metrics collection process")
    metrics_process.start()

    # Start workload. This calls stress-ng, which starts a child process to load one CPU at 53%
    stress_cmd = ["stress-ng", "--cpu", "1", "--cpu-load", f"{TEST_CPU_LOAD}", "--timeout", "30s"]
    print("Starting stress-ng")
    with subprocess.Popen(stress_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as stress:
        # stress = subprocess.Popen(stress_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(f"Process pid is {stress.pid}")
        stress_process = psutil.Process(stress.pid)

        # We need to wait for stress-ng to start it's child processes
        sleep(10)
        child_process = stress_process.children()[0]
        child_process_dict = child_process.as_dict()
        print(stress_process.children())
        stress_child_hash = hash_process(child_process_dict)
        print(f"Stress child hash is {stress_child_hash}")
        print(stress.stdout.read().decode("utf-8"))
        assert os.path.exists(db_path)

    # Wait for metrics collection to finish
    print("Waiting for metrics collection to finish")
    metrics_process.join(timeout=TIMEOUT_SECONDS)

    # Connect to the database and query for the CPU load
    engine = get_db_connection(db_path)
    session = Session(engine)

    print(f"Stress_child_hash: {stress_child_hash}")
    stress_cpu_percents = get_cpu_percents_for_pidHash(stress_child_hash, session)
    # Remove leading zeros from the list incase the stressor had not started yet
    trimed_stress_cpu_percents = remove_leading_zeros(stress_cpu_percents)

    logger.debug(f"Stress CPU percents: {trimed_stress_cpu_percents}")
    logger.debug(f"CPU table rows: {len(session.query(models.CPU.id).all())}")
    logger.debug(f"Process table rows: {len(session.query(models.SysProcess.pidHash).all())}")
    assert len(trimed_stress_cpu_percents) > 0
    avg_stress = sum(trimed_stress_cpu_percents) / len(trimed_stress_cpu_percents)

    # Test that the average CPU load is within 10% of the expected load
    assert avg_stress > (TEST_CPU_LOAD * 0.80)
    assert avg_stress < (TEST_CPU_LOAD * 1.20)


def remove_leading_zeros(_list: list) -> list:
    """Remove leading zeros from a list"""
    for i, item in enumerate(_list):
        if item != 0:
            return _list[i:]
    return _list
