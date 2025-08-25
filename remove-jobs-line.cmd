@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo Removing stray "fetchAPI('/jobs')" lines from all .html files...
for /r %%F in (*.html) do (
  >"%%F.tmp" (
    for /f "usebackq delims=" %%L in ("%%F") do (
      set "line=%%L"
      rem Drop any line containing either of these markers:
      echo(!line!| findstr /i /c:"fetchAPI('/jobs')" /c:"const jobs =" >nul || echo(!line!
    )
  )
  move /y "%%F.tmp" "%%F" >nul
  echo Cleaned: %%F
)
echo Done.
