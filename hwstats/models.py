from datetime import datetime

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
    pidHash: Mapped[int] = mapped_column(primary_key=True)
    createTime: Mapped[datetime] = mapped_column(DateTime)

    cpu: Mapped[list["CPU"]] = relationship(back_populates="process", cascade="all, delete-orphan")
    memory: Mapped[list["Memory"]] = relationship(
        back_populates="process", cascade="all, delete-orphan"
    )
    disk: Mapped[list["Disk"]] = relationship(
        back_populates="process", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"SysProcess(pidHash={self.pidHash}, name={self.name})"


class CPU(Base):
    """CPU metrics gathered from running system processes"""

    __tablename__ = "cpu"

    id: Mapped[int] = mapped_column(primary_key=True)
    pidHash: Mapped[int] = mapped_column(ForeignKey("system_process.pidHash"))
    cpuPercent: Mapped[float] = mapped_column()
    userTime: Mapped[float] = mapped_column()
    systemTime: Mapped[float] = mapped_column()
    threads: Mapped[int] = mapped_column()
    upTime: Mapped[float] = mapped_column()

    process: Mapped["SysProcess"] = relationship(back_populates="cpu")

    def __repr__(self) -> str:
        return f"CPU(id={self.id}, pidHash={self.pidHash})"


class Memory(Base):
    """Memory metrics gathered from running system processes"""

    __tablename__ = "memory"

    id: Mapped[int] = mapped_column(primary_key=True)
    pidHash: Mapped[int] = mapped_column(ForeignKey("system_process.pidHash"))
    memoryPercent: Mapped[float] = mapped_column()
    memoryInfo: Mapped[list[float]] = mapped_column()

    process: Mapped["SysProcess"] = relationship(back_populates="memory")

    def __repr__(self) -> str:
        return f"Memory(id={self.id}, pidHash={self.pidHash})"


class Disk(Base):
    """Disk metrics gathered from running system processes"""

    __tablename__ = "disk"

    id: Mapped[int] = mapped_column(primary_key=True)
    pidHash: Mapped[int] = mapped_column(ForeignKey("system_process.pidHash"))
    diskTime: Mapped[float] = mapped_column()
    diskIO: Mapped[list[float]] = mapped_column()
    process: Mapped["SysProcess"] = relationship(back_populates="disk")

    def __repr__(self) -> str:
        return f"Disk(id={self.id}, pidHash={self.pidHash})"


def build_cpu_from_process(process: Process) -> CPU:
    """Build CPU record object from a process"""
    return CPU(
        pidHash=hash(process),
        cpuPercent=process.cpu_percent(),
        systemTime=process.cpu_times().system,
        userTime=process.cpu_times().user,
    )


def build_memory_from_process(process: Process) -> Memory:
    """Build Memory record object from a process"""
    return Memory(
        pidHash=hash(process),
        memoryPercent=process.memory_percent(),
        memoryInfo=process.memory_info(),
    )


def build_sysprocess_from_process(process: Process) -> SysProcess:
    """Build a SysProcess record object from a process"""
    return SysProcess(
        pidHash=hash(process),
        pid=process.pid,
        name=process.name(),
        createTime=datetime.fromtimestamp(process.create_time()),
    )
