# Notificador de Senado TV en la nube (sin dejar nada encendido)

GitHub Actions ejecuta el script solo, cada 5 minutos, en los servidores de GitHub. No necesitás ninguna PC ni servidor.

## Pasos

1. **Bot de Telegram**: hablá con [@BotFather](https://t.me/BotFather), enviá `/newbot` y copiá el token.
2. **Chat ID**: escribile un mensaje a tu bot y abrí `https://api.telegram.org/bot<TOKEN>/getUpdates`; buscá `"chat":{"id": ...}`.
3. **Clave de YouTube**: en [Google Cloud Console](https://console.cloud.google.com/) creá un proyecto, activá "YouTube Data API v3" y generá una API key.
4. **Repositorio**: creá una cuenta en GitHub si no tenés, creá un repositorio **público** nuevo y subí todos estos archivos (incluida la carpeta `.github`). Usá "Add file → Upload files" y arrastrá la carpeta completa.
5. **Secretos**: en el repositorio, `Settings → Secrets and variables → Actions → New repository secret`. Creá tres:
   - `YOUTUBE_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
6. **Probar**: pestaña `Actions → Senado TV live notifier → Run workflow`, tildá "test" y ejecutá. Tiene que llegarte un mensaje a Telegram.

Desde ahí corre solo. No hace falta tocar nada más.

## Detalles a tener en cuenta
- **Repositorio público**: es lo que da minutos de ejecución ilimitados. Tus claves quedan en los Secrets, nadie las ve. En un repositorio privado el cupo gratis (2.000 min/mes) no alcanza para correr cada 5 minutos.
- **Demora**: GitHub ejecuta el cron cada ~5 minutos, pero a veces se atrasa varios minutos en horas de mucha carga. Contá con un aviso 2 a 10 minutos después de que empieza el vivo.
- **Inactividad**: GitHub puede desactivar los workflows programados de repositorios públicos sin actividad por 60 días. Si pasa, te llega un mail y se reactiva con un clic en la pestaña Actions.
- Cuota de YouTube: ~576 unidades por día de las 10.000 gratuitas.
