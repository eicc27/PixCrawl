Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

function cstr {
    param ([String] $s, [String] $fc, [String] $bc, [Boolean] $nl = 1)
    $arguments = @{}
    if($bc) {$arguments.BackgroundColor = $bc}
    if($fc) {$arguments.ForegroundColor = $fc}
    if(-not $nl) {$arguments.Nonewline = 1}
    Write-Host $s @arguments
}

function check_integrity {
    param ([String[]] $files)
    foreach ($file in $files) {
        if (-not (Test-Path $file)) {
            cstr "$file not in current working directory. Change to PixCrawl folder instead." "Red"
            exit
        }
    }
    cstr "File integrity check passed." "Green"
}

check_integrity "args.json", "check_browser.py", "cli.py", "crawler.py", "database.py",
"doujin.py", "downloader.py", "native_crawler.py", "pixcrawl.py", "pixiv_crawler.py",
"preinit.py", "startups.json", "strformat.py"

$path_310 = where.exe python | findstr.exe "310"
if (-not $path_310) {
    cstr "No python 3.10 installed." "Red"
    exit
}

if (-not($args -contains "--nocheck")) {
    $check = Read-Host "Run pre-initialization and check browser status? [Y/n]"
    if (($check -eq 'y') -or ($check -eq 'Y') -or ($check -eq '')) {
        & $path_310 ".\preinit.py"
    }
}

try {
    .\venv\Scripts\Activate.ps1
    cstr "Program has been successfully started." "Green"
    .\venv\Scripts\python.exe .\pixcrawl.py $args
}
catch [System.SystemException] {
    cstr "PixCrawl main funtion start failed. Try run with pre-initialization first." "Red"
}


