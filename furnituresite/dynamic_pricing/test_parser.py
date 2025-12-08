import re
import time

# Імпорт може працювати і так, і так, залежно від версії
try:
    from duckduckgo_search import DDGS
except ImportError:
    # Якщо встановили як ddgs
    from ddgs import DDGS

# --- НАЛАШТУВАННЯ ---
TEST_ARTICLE = "ST-0002"
TEST_SITE = "rozetka.com.ua"


# --------------------

def debug_ddg_lib():
    print(f"\n--- ПОЧАТОК ТЕСТУ (DDGS Updated) ---")
    print(f"🌍 Сайт: {TEST_SITE}")
    print(f"📦 Артикул: {TEST_ARTICLE}")

    query = f"site:{TEST_SITE} \"{TEST_ARTICLE}\""
    print(f"🚀 Запит: {query}")

    try:
        print("⏳ Звертаємось до DuckDuckGo...")

        # У нових версіях краще не вказувати backend, бібліотека сама вибере робочий
        # region='ua-uk' - важливо для українських цін
        results_gen = DDGS().text(query, region='ua-uk', max_results=5)

        # Перетворюємо генератор у список одразу, щоб перевірити наявність даних
        results_list = list(results_gen)

        if not results_list:
            print("⚠️ Результатів не знайдено (порожній список).")
            print("   Можливі причини: артикул не проіндексовано або IP тимчасово обмежено.")
            return

        print(f"📄 Отримано результатів: {len(results_list)}")

        full_text = ""
        for res in results_list:
            title = res.get('title', 'No Title')
            # Бібліотека може повертати body, content або snippet
            body = res.get('body') or res.get('content') or res.get('snippet') or ""
            print(f"   🔹 Знайдено: {title}")
            full_text += " " + body

        print("\n🔍 Скануємо текст на наявність цін...")

        # Регулярка
        price_matches = re.findall(r'(\d{1,3}(?:\s\d{3})*)\s?(?:грн|UAH|₴)', full_text, re.IGNORECASE)

        valid_prices = []
        for p_str in price_matches:
            clean_price = p_str.replace(' ', '').replace('\xa0', '')
            if clean_price.isdigit():
                price = float(clean_price)
                if 50 < price < 100000:
                    valid_prices.append(price)
                    print(f"   ➡️ Знайдено число: {price}")

        if valid_prices:
            min_price = min(valid_prices)
            print(f"\n✅ УСПІХ! Мінімальна ціна: {min_price} грн")
        else:
            print("\n⚠️ Ціни в тексті не знайдено.")

    except Exception as e:
        print(f"❌ Критична помилка: {e}")


if __name__ == "__main__":
    debug_ddg_lib()