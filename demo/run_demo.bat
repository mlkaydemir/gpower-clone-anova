@echo off
chcp 65001 > nul
cls
echo ======================================================================
echo       YZM301 TEARDOWN SPRINT - G*POWER CLONE DEMO (ANOVA ONE-WAY)
echo ======================================================================
echo.
timeout /t 2 > nul

echo [ADIM 1] Sürüm Sorgusu: gpower-clone --version
echo Komut: .\gpower-clone.bat --version
call .\gpower-clone.bat --version
echo.
timeout /t 3 > nul

echo [ADIM 2] A Priori Örneklem Hesabı (Public Reference Vector: 5 grup, f=0.25)
echo Komut: .\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5
call .\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.95 --groups 5
echo.
timeout /t 3 > nul

echo [ADIM 3] Hata ve Sınır Değer Doğrulaması (Power ^<= Alpha)
echo Komut: .\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.03 --groups 5
call .\gpower-clone.bat --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.03 --groups 5
echo.
timeout /t 3 > nul

echo [ADIM 4] Diferansiyel Test ve Oracle Doğrulaması (35 Kâhin Vektörü)
echo Komut: python -m pytest tests/test_differential.py -v
python -m pytest tests/test_differential.py -v
echo.
timeout /t 3 > nul

echo [ADIM 5] Bonus: MCP Eşdeğerlik Testi
echo Komut: python -m pytest tests/test_mcp_equivalence.py -v
python -m pytest tests/test_mcp_equivalence.py -v
echo.
timeout /t 3 > nul

echo [ADIM 6] Bonus: Klinik AI Ajanı - 10 Soruluk Doğal Dil Testi
echo Komut: python -m src.agent --eval
python -m src.agent --eval
echo.

echo ======================================================================
echo DEMO BAŞARIYLA TAMAMLANDI!
echo ======================================================================
pause
