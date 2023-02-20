# hw-stats
Python utility for Linux to track system hardware usage metrics

## How to contribute
### Quick start
To start contributing in a Linux enviroonemt simply run the following:
```bash
git clone git@github.com:cohenm0/hw-stats.git
cd hw-stats
make
```

### Setting up a dev environment on Windows
For a windows 10 or 11 based development platform the following guides can be used to set up the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) (or WSL) and then set up a [python development environment](https://learn.microsoft.com/en-us/windows/python/web-frameworks) that uses vscode. We also use [pyenv](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv) to allow for development and testing on multiple versions of python, and use [pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today) to manage the development environment and its dependencies.


## `psutil` demo
Here's a simple example to find all running processes using `ipython`:
```python
import psutil
for _process in psutil.process_iter():
    if _process.status() is not psutil.STATUS_SLEEPING:
        print(_process)
```
