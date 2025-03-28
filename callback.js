export default function handler(req, res) {
  const code = req.query.code;
  console.log("[AliExpress] Received code:", code);

  if (code) {
    res.status(200).send(`✅ Ваш AliExpress OAuth Code: <b>${code}</b><br><br>Скопируй и вставь его в чат, чтобы получить access_token.`);
  } else {
    res.status(400).send("❌ Code не найден в URL. Попробуй снова или проверь redirect_uri.");
  }
}