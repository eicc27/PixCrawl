Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
Set-Location .\venv\Scripts
.\Activate.ps1
Set-Location ..
Set-Location ..
.\venv\Scripts\python.exe .\pixcrawl.py $args