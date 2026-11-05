# Notificador de vivos de Senado TV → Telegram

Avisa por Telegram cuando el canal https://www.youtube.com/@SenadoTVArgentina/streams empieza una transmisión en vivo.

## Cómo funciona
Cada tanto consulta la lista de videos subidos del canal (donde aparecen los vivos) y pregunta a YouTube cuáles tienen estado "live". Si hay uno nuevo, manda el título y el link a Telegram. Guarda en `state.json` lo ya avisado para no repetir. Cada revisión gasta 2 unidades de la cuota diaria gratuita (10.000), así que revisar cada 2 minutos consume ~1.440 por día.

## Configuración (una sola vez)

1. **Bot de Telegram**: hablá con [@BotFather](https://t.me/BotFather), enviá `/newbot` y copiá el token.
2. **Chat ID**: escribile cualquier mensaje a tu bot y abrí `https://api.telegram.org/bot<TOKEN>/getUpdates`; buscá `"chat":{"id": ...}`. Para un grupo o canal, agregá el bot (en canales, como administrador) y usá su id (suele empezar con `-100`).
3. **Clave de YouTube**: en [Google Cloud Console](https://console.cloud.google.com/) creá un proyecto, activá "YouTube Data API v3" y generá una API key.
4. Copiá `.env.example` a `.env` y completá los valores.
5. `pip install requests`

## Uso
```
python senado_live_notifier.py --test    # verifica que llegue el mensaje a Telegram
python senado_live_notifier.py --loop    # queda corriendo y revisa cada 2 minutos
```

Para dejarlo funcionando solo, usá `--loop` en un servidor/Raspberry/PC siempre encendida (con `systemd`, `pm2` o `screen`), o ejecutá una sola revisión cada 2-5 minutos con cron:
```
*/3 * * * * cd /ruta/al/proyecto && python3 senado_live_notifier.py
```

## Limitaciones
- Puede haber un retraso de 1 a 3 minutos entre que empieza el vivo y el aviso (por el intervalo y porque YouTube tarda en listarlo).
- No avisa de vivos programados que aún no empezaron, solo de los que ya están en directo.
