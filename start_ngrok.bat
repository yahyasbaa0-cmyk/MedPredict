@echo off
echo Lancement du tunnel securise (Cloudflare) vers localhost:8000...
echo.
echo ================================================================
echo Cherchez la ligne qui ressemble a :
echo "https://quelque-chose.trycloudflare.com"
echo Copiez ce lien et mettez-le dans Twilio !
echo ================================================================
echo.
.\cloudflared.exe tunnel --url http://localhost:8000
pause
