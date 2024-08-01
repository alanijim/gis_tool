SET PLUGINNAME=SlaacGatheringTool
SET HOME=%userprofile%
SET TARGET=%userprofile%\.qgis2\python\plugins\%PLUGINNAME%
SET EXP_TARGET=%userprofile%\.qgis2\python\expressions
if not exist "%TARGET%\" mkdir "%TARGET%"
pyrcc4 -o resources.py resources.qrc
FOR %%I IN (%cd%\*.py) DO copy "%%I" "%TARGET%\%%~nI%%~xI"
FOR %%I IN (%cd%\*.png) DO copy "%%I" "%TARGET%\%%~nI%%~xI"
FOR %%I IN (%cd%\*.txt) DO copy "%%I" "%TARGET%\%%~nI%%~xI"
FOR %%I IN (%cd%\*.ui) DO copy "%%I" "%TARGET%\%%~nI%%~xI"
FOR %%I IN (%cd%\expressions\*.py) DO copy "%%I" "%EXP_TARGET%\%%~nI%%~xI"
xcopy %cd%\i18n %TARGET%\i18n /E /Y /I
