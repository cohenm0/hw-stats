# hw-stats
Python utility for Linux to track system hardware usage metrics

Here's a simple example to find all running processes using `ipython`:
```python
import psutil
for _process in psutil.process_iter():
    if _process.status() is not psutil.STATUS_SLEEPING:
        print(_process)
```