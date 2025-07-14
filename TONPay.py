async def check_ton_payment(expected_amount_nano: str, comment: str) -> bool:
    """Проверка платежа в сети TON с подробным логированием"""
    print(f"\n🔍 [Проверка платежа] Ожидаем: {expected_amount_nano} nanoTON, комментарий: '{comment}'")
    
    try:
        expected = int(expected_amount_nano)
        tolerance = max(int(expected * 0.01), 1000000)
        print(f"🔢 Допустимый диапазон: {expected - tolerance} - {expected + tolerance} nanoTON")
        
        params = {
            'address': str(TON_WALLET),
            'limit': 20,
            'api_key': str(TON_API_TOKEN),
            'archival': 'true'
        }
        
        print("🌐 Запрашиваем транзакции с параметрами:")
        print(f" - Адрес: {TON_WALLET}")
        print(f" - Лимит: 20")
        
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.get(
                    f"{TON_API_BASE}getTransactions",
                    params=params,
                    timeout=20
                )
                
                print(f"📡 Ответ API: статус {response.status}")
                
                if response.status != 200:
                    print(f"❌ Ошибка API: HTTP {response.status}")
                    return False
                
                data = await response.json()
                print(f"📊 Получено транзакций: {len(data.get('result', []))}")
                
                if not data.get('ok', False):
                    error_msg = data.get('error', 'Неизвестная ошибка API')
                    print(f"❌ Ошибка API: {error_msg}")
                    return False
                
                for tx in data.get('result', []):
                    in_msg = tx.get('in_msg', {})
                    
                    # Обработка суммы
                    tx_value = 0
                    try:
                        value = in_msg.get('value')
                        if value is not None:
                            tx_value = int(float(value))
                    except (TypeError, ValueError):
                        continue
                    
                    # Обработка комментария
                    tx_comment = str(in_msg.get('message', '')).strip()
                    
                    print(f"\n🔎 Проверяем транзакцию:")
                    print(f" - Хэш: {tx.get('hash')}")
                    print(f" - Сумма: {tx_value} nanoTON")
                    print(f" - Комментарий: '{tx_comment}'")
                    print(f" - Дата: {tx.get('utime')}")
                    
                    # Проверка совпадения
                    amount_match = abs(tx_value - expected) <= tolerance
                    comment_match = tx_comment == comment.strip()
                    
                    print(f"🔹 Совпадение суммы: {'✅' if amount_match else '❌'}")
                    print(f"🔹 Совпадение комментария: {'✅' if comment_match else '❌'}")
                    
                    if amount_match and comment_match:
                        print(f"\n🎉 Найден подходящий платеж!")
                        print(f" - Получено: {tx_value} nanoTON")
                        print(f" - Ожидалось: {expected} nanoTON (±{tolerance})")
                        print(f" - Комментарий: '{tx_comment}'")
                        print(f" - Время: {tx.get('utime')}")
                        return True
                
                print("\n🔍 Подходящих платежей не найдено")
                return False
                
            except asyncio.TimeoutError:
                print("⏱️ Таймаут при запросе к TON API")
                return False
            except aiohttp.ClientError as e:
                print(f"🌐 Ошибка сети: {str(e)}")
                return False
    
    except Exception as e:
        print(f"💥 Критическая ошибка: {type(e).__name__}: {str(e)}")
        return False
