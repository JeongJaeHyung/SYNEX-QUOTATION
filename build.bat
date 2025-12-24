@echo off
chcp 65001 >nul
echo ========================================
echo JLT Quotation System - Build Script
echo ========================================
echo.

:: 가상환경 활성화
call .venv\Scripts\activate.bat

:: 기존 빌드 폴더 삭제
echo [1/4] 기존 빌드 폴더 정리 중...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

:: PyInstaller 빌드
echo [2/4] PyInstaller로 exe 빌드 중... (시간이 걸릴 수 있습니다)
pyinstaller build.spec --noconfirm

:: Playwright 브라우저 복사
echo [3/4] Playwright 브라우저 복사 중...
set BROWSERS_SRC=%LOCALAPPDATA%\ms-playwright
set BROWSERS_DST=dist\JLT_Quotation\browsers

if not exist "%BROWSERS_DST%" mkdir "%BROWSERS_DST%"

:: chromium 폴더 복사
xcopy "%BROWSERS_SRC%\chromium-1200" "%BROWSERS_DST%\chromium-1200" /E /I /H /Y >nul
echo    - chromium-1200 복사 완료

:: ffmpeg 복사 (동영상 처리용, 필요시)
xcopy "%BROWSERS_SRC%\ffmpeg-1011" "%BROWSERS_DST%\ffmpeg-1011" /E /I /H /Y >nul
echo    - ffmpeg-1011 복사 완료

echo.
echo [4/4] 빌드 완료!
echo.
echo ========================================
echo 결과물 위치: dist\JLT_Quotation\
echo 실행 파일: dist\JLT_Quotation\JLT_Quotation.exe
echo ========================================
echo.
pause
