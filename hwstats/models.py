from datetime import datetime

import psutil
import xxhash
from psutil import Process
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime


class Base(DeclarativeBase):
    pass


class SysProcess(Base):
    """Processes that have run on the system"""

    __tablename__ = "system_process"

    # id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    pid: Mapped[int] = mapped_column()
    pidHash: Mapped[str] = mapped_column(primary_key=True)
    createTime: Mapped[datetime] = mapped_column(DateTime)

    cpu: Mapped[list["CPU"]] = relationship(back_populates="process", cascade="all, delete-orphan")
    memory: Mapped[list["Memory"]] = relationship(
        back_populates="process", cascade="all, delete-orphan"
    )
    disk: Mapped[list["Disk"]] = relationship(
        back_populates="process", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"SysProcess(pidHash={self.pidHash}, name={self.name}, pid={self.pid}, createTime={self.createTime}, cpu={self.cpu}, memory={self.memory},disk={self.disk})"


class CPU(Base):
    """CPU metrics gathered from running system processes"""

    __tablename__ = "cpu"

    id: Mapped[int] = mapped_column(primary_key=True)
    pidHash: Mapped[str] = mapped_column(ForeignKey("system_process.pidHash"))
    cpuPercent: Mapped[float] = mapped_column()
    userTime: Mapped[float] = mapped_column()
    systemTime: Mapped[float] = mapped_column()
    threads: Mapped[int] = mapped_column()
    # idleTime: Mapped[float] = mapped_column()
    measurementTime: Mapped[datetime] = mapped_column(DateTime)

    process: Mapped["SysProcess"] = relationship(back_populates="cpu")

    def __repr__(self) -> str:
        return f"CPU(id={self.id}, pidHash={self.pidHash}, cpuPercent={self.cpuPercent}, userTime={self.userTime}, systemTime={self.systemTime}, threads={self.threads}, measuremetTime={self.measurementTime}, process={self.process})"


class Memory(Base):
    """Memory metrics gathered from running system processes"""

    __tablename__ = "memory"

    id: Mapped[int] = mapped_column(primary_key=True)
    pidHash: Mapped[str] = mapped_column(ForeignKey("system_process.pidHash"))
    memoryPercent: Mapped[float] = mapped_column(default=0.0)
    memoryRSS: Mapped[int] = mapped_column()
    measurementTime: Mapped[datetime] = mapped_column(DateTime)

    process: Mapped["SysProcess"] = relationship(back_populates="memory")

    def __repr__(self) -> str:
        return f"Memory(id={self.id}, pidHash={self.pidHash}, memoryPercent={self.memoryPercent}, memoryRSS={self.memoryRSS}, measeurmentTime={self.measurementTime}, process={self.process})"


class Disk(Base):
    """Disk metrics gathered from running system processes"""

    __tablename__ = "disk"

    id: Mapped[int] = mapped_column(primary_key=True)
    pidHash: Mapped[str] = mapped_column(ForeignKey("system_process.pidHash"))
    # diskTime: Mapped[float] = mapped_column()
    diskRead: Mapped[int] = mapped_column()
    diskWrite: Mapped[int] = mapped_column()
    measurementTime: Mapped[datetime] = mapped_column(DateTime)

    process: Mapped["SysProcess"] = relationship(back_populates="disk")

    def __repr__(self) -> str:
        return f"Disk(id={self.id}, pidHash={self.pidHash}, diskRead={self.diskRead}, diskWrite={self.diskWrite}, measurementTime={self.measurementTime}, process={self.process})"


def hash_process(process: Process) -> str:
    """Fast, low collision hash of a process"""
    return xxhash.xxh3_64(str(process).encode("utf-8")).hexdigest()


def build_cpu_from_process(process: Process) -> CPU:
    """Build CPU record object from a process"""
    return CPU(
        pidHash=hash_process(process),
        cpuPercent=process.cpu_percent(),
        systemTime=process.cpu_times().system,
        userTime=process.cpu_times().user,
        threads=process.num_threads(),
        # idleTime=process.cpu_times().idle,
        measurementTime=datetime.now(),
    )


def build_memory_from_process(process: Process) -> Memory:
    """Build Memory record object from a process"""
    return Memory(
        pidHash=hash_process(process),
        memoryPercent=process.memory_percent(),
        memoryRSS=process.memory_info().rss,
        measurementTime=datetime.now(),
    )


def build_disk_from_process(process: Process) -> Disk:
    """Build Disk record object from a process"""
    try:
        _diskRead = process.io_counters().read_count
    except (PermissionError, psutil.AccessDenied):
        _diskRead = 0
    try:
        _diskWrite = process.io_counters().write_count
    except (PermissionError, psutil.AccessDenied):
        _diskWrite = 0
    return Disk(
        pidHash=hash_process(process),
        diskRead=_diskRead,
        diskWrite=_diskWrite,
        measurementTime=datetime.now(),
    )


def build_sysprocess_from_process(process: Process) -> SysProcess:
    """Build a SysProcess record object from a process"""
    return SysProcess(
        pidHash=hash_process(process),
        pid=process.pid,
        name=process.name(),
        createTime=datetime.fromtimestamp(process.create_time()),
    )
