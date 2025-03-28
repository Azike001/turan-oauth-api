# 🚀 TURAN: Автозапуск бота и SSH при старте Termux с Telegram-оповещением IP

# Включить блокировку сна
termux-wake-lock

# Запустить SSH-сервер, если не запущен
pgrep sshd > /dev/null || sshd

# Получить текущий IP
IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -n 1)

# Вывести IP в терминал
echo -e "\e[1;36m📡 IP устройства: $IP\e[0m"

# Отправить IP в Telegram
curl -s -X POST https://api.telegram.org/bot8080091792:AAED9X1dxlMDy3Xca5qwjGlzRIS31VGAkdA/sendMessage \
  -d chat_id=6608247548 \
  -d text="📡 TURAN IP: $IP\n🤖 Бот автоматически запущен."

# Запустить бота, если он не запущен
if [ -f ~/bot.py ]; then
  echo "⏳ Проверка запуска бота TURAN..."
  pgrep -f bot.py > /dev/null || turan
fi

