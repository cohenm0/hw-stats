import psutil

import hwstats.models


def test_sys_process_builder():
    """Test the SysProcess builder"""
    process = hwstats.models.build_sysprocess_from_process(psutil.Process())
    assert isinstance(process, hwstats.models.SysProcess)


def test_cpu_builder():
    """Test the SysProcess builder"""
    process = hwstats.models.build_cpu_from_process(psutil.Process())
    assert isinstance(process, hwstats.models.CPU)


def test_memory_builder():
    """Test the SysProcess builder"""
    process = hwstats.models.build_memory_from_process(psutil.Process())
    assert isinstance(process, hwstats.models.Memory)


def test_disk_builder():
    """Test the SysProcess builder"""
    process = hwstats.models.build_disk_from_process(psutil.Process())
    assert isinstance(process, hwstats.models.Disk)
