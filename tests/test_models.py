import psutil
import xxhash

import hwstats.models


def test_sys_process_builder():
    """Test the SysProcess builder"""
    process_dict = psutil.Process().as_dict()
    id_str = f"{process_dict['pid']}, {process_dict['name']}, {process_dict['create_time']}"
    process_dict["pidHash"] = xxhash.xxh64(id_str).hexdigest()
    process = hwstats.models.build_sysprocess_from_process(process_dict)
    assert isinstance(process, hwstats.models.SysProcess)


def test_cpu_builder():
    """Test the SysProcess builder"""
    process_dict = psutil.Process().as_dict()
    id_str = f"{process_dict['pid']}, {process_dict['name']}, {process_dict['create_time']}"
    process_dict["pidHash"] = xxhash.xxh64(id_str).hexdigest()
    process = hwstats.models.build_cpu_from_process(process_dict)
    assert isinstance(process, hwstats.models.CPU)


def test_memory_builder():
    """Test the SysProcess builder"""
    process_dict = psutil.Process().as_dict()
    id_str = f"{process_dict['pid']}, {process_dict['name']}, {process_dict['create_time']}"
    process_dict["pidHash"] = xxhash.xxh64(id_str).hexdigest()
    process = hwstats.models.build_memory_from_process(process_dict)
    assert isinstance(process, hwstats.models.Memory)


def test_disk_builder():
    """Test the SysProcess builder"""
    process_dict = psutil.Process().as_dict()
    id_str = f"{process_dict['pid']}, {process_dict['name']}, {process_dict['create_time']}"
    process_dict["pidHash"] = xxhash.xxh64(id_str).hexdigest()
    process = hwstats.models.build_disk_from_process(process_dict)
    assert isinstance(process, hwstats.models.Disk)
