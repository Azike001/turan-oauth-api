# 🚀 TURAN: запуск Telegram-бота
turan() {
  cd ~
  termux-wake-lock
  nohup python bot.py > ~/bot.log 2>&1 &
  echo "🚀 TURAN бот запущен в фоне!"
}

# 🛑 TURAN: остановка бота
turan-stop() {
  pkill -f bot.py
  rm -f ~/bot.lock
  echo "⛔ TURAN бот остановлен и lock-файл удалён."
}

# 📊 TURAN: статус бота
turan-status() {
  if pgrep -f bot.py > /dev/null; then
    echo "✅ Бот работает!"
  else
    echo "❌ Бот не запущен."
  fi
}

# 📄 TURAN: лог автопостинга
turan-log() {
  tail -f ~/bot.log
}

