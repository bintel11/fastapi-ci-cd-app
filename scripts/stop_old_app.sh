Get-Process python | Where-Object {$_.Path -like "*app.py*"} | Stop-Process
