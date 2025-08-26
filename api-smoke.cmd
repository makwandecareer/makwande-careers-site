@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: Frontend domain (tests the Render rewrite)
set "BASE=https://autoapplyapp-mobile.onrender.com"

:: Status codes that indicate connectivity (OK even if auth required / wrong method)
set "OKCODES=200 201 202 204 301 302 400 401 403 405"

set /a OK=0, WARN=0, FAIL=0

echo === API Smoke via frontend: %BASE% ===

call :CHECK GET  /api/health
call :CHECK GET  /api/jobs
call :CHECK GET  /api/bursaries
call :CHECK GET  /api/applications
call :CHECK GET  /api/subscription
call :CHECK GET  /api/recruiter/jobs

:: POST endpoints (safe body {} so we don't send real data; expect 400/401/403/405)
call :CHECK POST /api/revamp
call :CHECK POST /api/cover_letter
call :CHECK POST /api/signup
call :CHECK POST /api/login
call :CHECK POST /api/subscribe
call :CHECK POST /api/subscription/cancel
call :CHECK POST /api/recruiter/jobs
call :CHECK POST /api/bursaries/apply
call :CHECK POST /api/bursaries/approve
call :CHECK POST /api/partners/contact
call :CHECK POST /api/universities/partner

echo.
echo === Summary ===
echo   OK:   %OK%
echo   WARN: %WARN%   (404 = route not found but rewrite worked)
echo   FAIL: %FAIL%   (no response / network error)
exit /b 0

:CHECK
:: %1=METHOD  %2=PATH
set "METHOD=%~1"
set "PATH=%~2"

if /I "%METHOD%"=="GET" (
  for /f %%C in ('curl -s -o NUL -w "%%{http_code}" "%BASE%%PATH%"') do set "CODE=%%C"
) else (
  for /f %%C in ('curl -s -o NUL -w "%%{http_code}" -H "Content-Type: application/json" -d "{}" -X POST "%BASE%%PATH%"') do set "CODE=%%C"
)

:: Treat certain codes as OK, 404 as WARN, everything else fail
echo %OKCODES% | findstr /r "\<%CODE%\>" >nul && (
  echo [OK  ] %METHOD% %PATH%  -> %CODE%
  set /a OK+=1
  goto :eof
)

if "%CODE%"=="404" (
  echo [WARN] %METHOD% %PATH%  -> 404 (route not found; rewrite still hit frontend)
  set /a WARN+=1
  goto :eof
)

:: If we got nothing, curl likely failed (network/DNS/SSL)
if "%CODE%"=="" (
  echo [FAIL] %METHOD% %PATH%  -> no response
  set /a FAIL+=1
  goto :eof
)

echo [FAIL] %METHOD% %PATH%  -> %CODE%
set /a FAIL+=1
goto :eof
