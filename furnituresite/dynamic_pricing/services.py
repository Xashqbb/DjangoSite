import re
import time
import random
import traceback
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib3

# Вимикаємо попередження про SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from curl_cffi import requests as cffi_requests

    HAS_CURL = True
except ImportError:
    HAS_CURL = False
    import requests


class PricingEngine:
    def __init__(self, product_article, product_name, current_price, stock_qty):
        self.article = str(product_article).strip()
        self.product_name = str(product_name).strip()
        self.my_price = float(current_price)
        self.stock = int(stock_qty)

        self.MAX_PAGES = 3
        self.DEBUG_MODE = True

        self.category = self._extract_category_keyword()
        self.min_valid_price = self.my_price * 0.4  # Розширив діапазон (акції)
        self.max_valid_price = self.my_price * 3.0

        # Сесія
        if HAS_CURL:
            # Зміна профілю на chrome110 (часто менш підозрілий для Cloudflare)
            self.session = cffi_requests.Session(impersonate="chrome110")
        else:
            self.session = requests.Session()
            self.session.headers.update(self._get_headers())

    def _get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }

    def _extract_category_keyword(self):
        priority_words = ['стіл', 'стол', 'шафа', 'тумба', 'крісло', 'ліжко', 'комод', 'полка', 'стелаж']
        name_lower = self.product_name.lower()
        for word in priority_words:
            if word in name_lower: return word.capitalize()
        parts = self.product_name.split()
        for p in parts:
            if len(p) > 3: return p
        return ""

    def _generate_smart_queries(self):
        cat = self.category
        art = self.article
        art_clean = art.replace('-', '').replace(' ', '')

        queries = [
            f"{cat} {art}",  # Стіл ST-0015
            art,  # ST-0015
            art_clean,  # ST0015
        ]
        return list(dict.fromkeys(queries))

    def _make_request(self, url, source_name="unknown", use_session=True):
        print(f"      🌐 GET: {url}")
        # Випадкова затримка "людини"
        time.sleep(random.uniform(3.5, 7.0))

        try:
            if use_session and HAS_CURL:
                response = self.session.get(url, timeout=30)
            elif HAS_CURL:
                response = cffi_requests.get(url, impersonate="chrome110", headers=self._get_headers(), timeout=30)
            else:
                response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                if "Just a moment" in response.text or "Captcha" in response.text:
                    print(f"      ⚠️ BLOCK (Captcha) on {source_name}")
                    return None
                return BeautifulSoup(response.text, 'html.parser')
            elif response.status_code == 403:
                print(f"      ⚠️ Forbidden (403) on {source_name}")
                return None
            else:
                print(f"      ⚠️ Status: {response.status_code}")

        except Exception as e:
            print(f"      ⚠️ Net Err: {str(e)[:50]}")

        return None

    def _clean_price(self, text):
        if not text: return None
        # Залишаємо цифри
        clean = re.sub(r'[^\d]', '', str(text))
        if not clean: return None
        try:
            val = float(clean)
            if self.min_valid_price <= val <= self.max_valid_price:
                return val
        except:
            pass
        return None

    def _text_radar_search(self, soup, source_url):
        """Пошук артикулу в тексті сторінки (для Prom/Epicentr)"""
        if not soup: return None
        variations = [
            self.article.lower(),
            self.article.lower().replace('-', ''),
            self.article.lower().replace('-', ' ')
        ]

        all_text = soup.get_text(" ", strip=True).lower()

        # Швидка перевірка: чи є артикул взагалі на сторінці?
        if not any(v in all_text for v in variations):
            return None

        # Якщо є, шукаємо детальніше
        found_prices = []
        all_text_nodes = soup.find_all(string=True)

        for text_node in all_text_nodes:
            txt_lower = text_node.lower()
            if any(v in txt_lower for v in variations):
                parent = text_node.parent
                # Піднімаємось на 5 рівнів
                for _ in range(5):
                    if not parent: break
                    block_text = parent.get_text(separator=' ', strip=True)
                    # Шукаємо "ціна... грн"
                    price_matches = re.findall(r'(\d[\d\s]*)\s*(?:грн|₴|UAH)', block_text, re.IGNORECASE)

                    for pm in price_matches:
                        price = self._clean_price(pm)
                        if price:
                            found_prices.append(price)
                            break
                    if found_prices: break
                    parent = parent.parent

        if found_prices:
            return min(found_prices)
        return None

    # --- ROZETKA ---
    def check_rozetka(self):
        print(f"🔍 Rozetka:")
        base_url = "https://rozetka.com.ua"

        # "Прогрів" з іншим хедером
        try:
            self.session.headers.update({'Referer': 'https://rozetka.com.ua/'})
            self.session.get(f"{base_url}/ua/", timeout=15)
        except:
            pass

        for query in self._generate_smart_queries():
            # Якщо один раз зловили бан, припиняємо мучити цей запит
            stop_search = False
            for page in range(1, self.MAX_PAGES + 1):
                if stop_search: break

                # Стандартний пошук
                url = f"{base_url}/ua/search/?text={quote(query)}&page={page}"
                soup = self._make_request(url, "rozetka")

                if not soup:
                    # Спроба "План Б": Мобільний API пошук (іноді пропускає)
                    print("      🔄 Trying API fallback...")
                    api_url = f"https://search.rozetka.com.ua/search/api/v6/?text={quote(query)}&page={page}&lang=ua"
                    try:
                        resp = self.session.get(api_url, timeout=20)
                        if resp.status_code == 200:
                            data = resp.json()
                            goods = data.get('data', {}).get('goods', [])
                            for g in goods:
                                title = g.get('title', '').lower()
                                if self.article.lower().replace('-', '') in title.replace('-', '').replace(' ', ''):
                                    p = self._clean_price(g.get('price'))
                                    if p:
                                        print(f"      ✅ API Found: {p} грн")
                                        return p
                    except:
                        pass
                    stop_search = True
                    break

                price = self._text_radar_search(soup, base_url)
                if price: return price

                # Специфічний пошук для розетки (data-goods-id)
                tiles = soup.select('.goods-tile')
                for tile in tiles:
                    t_text = tile.get_text().lower()
                    if self.article.lower().replace('-', '') in t_text.replace('-', ''):
                        p_el = tile.select_one('.goods-tile__price-value')
                        if p_el:
                            p = self._clean_price(p_el.get_text())
                            if p: return p

                if "Нічого не знайдено" in soup.get_text():
                    break
        return None

    # --- EPICENTR ---
    def check_epicentr(self):
        print(f"🔍 Epicentr:")
        base_url = "https://epicentrk.ua"
        for query in self._generate_smart_queries():
            for page in range(1, self.MAX_PAGES + 1):
                url = f"{base_url}/ua/search/?q={quote(query)}&page={page}"
                soup = self._make_request(url, "epicentr")
                if not soup: break
                price = self._text_radar_search(soup, base_url)
                if price: return price
                if not soup.select('.card, .columns'): break
        return None

    # --- PROM ---
    def check_prom(self):
        print(f"🔍 Prom:")
        base_url = "https://prom.ua"
        for query in self._generate_smart_queries():
            for page in range(1, self.MAX_PAGES + 1):
                url = f"{base_url}/ua/search?search_term={quote(query)}&page={page}"
                soup = self._make_request(url, "prom")
                if not soup: break
                price = self._text_radar_search(soup, base_url)
                if price: return price
        return None

    # --- KASTA (NEW STRING-SEARCH METHOD) ---
    def check_kasta(self):
        print(f"🔍 Kasta:")
        base_url = "https://kasta.ua"

        for query in self._generate_smart_queries():
            for page in range(1, self.MAX_PAGES + 1):
                url = f"{base_url}/uk/search/?text={quote(query)}&page={page}"
                soup = self._make_request(url, "kasta")
                if not soup: break

                # --- НОВИЙ МЕТОД: Глобальний пошук в JSON рядком ---
                # Ми не парсимо структуру, ми шукаємо текст артикулу в сирому JSON
                try:
                    script_tag = soup.find('script', id='__NEXT_DATA__')
                    if script_tag:
                        raw_json = script_tag.string
                        if not raw_json: continue

                        # Нормалізація для пошуку
                        search_art = self.article.lower().replace('-', '')  # st0015
                        json_lower = raw_json.lower()

                        # 1. Чи є взагалі артикул в даних сторінки?
                        if search_art in json_lower:
                            # 2. Якщо є, спробуємо витягнути список товарів "грубою силою"
                            data = json.loads(raw_json)
                            # Шукаємо список 'docs' будь-де в структурі
                            # (Це рекурсивний пошук ключа 'docs' або 'items')
                            found_price = self._find_price_in_json_recursively(data, search_art)
                            if found_price:
                                print(f"      💾 Kasta JSON Found: {found_price} грн")
                                return found_price

                except Exception as e:
                    print(f"      ⚠️ Kasta JSON Err: {e}")

                # Фолбек: звичайний радар
                price = self._text_radar_search(soup, base_url)
                if price: return price
        return None

    def _find_price_in_json_recursively(self, data, target_art_clean):
        """Рекурсивно шукає об'єкт товару з потрібним артикулом в JSON"""
        if isinstance(data, dict):
            # Перевіряємо чи це товар
            title = str(data.get('title', '')).lower().replace('-', '').replace(' ', '')
            sku = str(data.get('sku', '')).lower().replace('-', '').replace(' ', '')

            # Якщо це наш товар
            if target_art_clean in title or target_art_clean in sku:
                # Шукаємо ціну
                p = data.get('price') or data.get('final_price') or data.get('price_final')
                clean_p = self._clean_price(p)
                if clean_p: return clean_p

            # Йдемо вглиб
            for k, v in data.items():
                res = self._find_price_in_json_recursively(v, target_art_clean)
                if res: return res

        elif isinstance(data, list):
            for item in data:
                res = self._find_price_in_json_recursively(item, target_art_clean)
                if res: return res

        return None

    def calculate(self):
        print(f"\n🚀 SCAN START: {self.product_name} [{self.article}]")
        results = []

        try:
            # Черговість: Спочатку ті, що працюють добре
            if p := self.check_epicentr(): results.append({'source': 'Epicentr', 'price': p})
            if p := self.check_prom(): results.append({'source': 'Prom', 'price': p})
            if p := self.check_kasta(): results.append({'source': 'Kasta', 'price': p})

            # Розетка остання, бо найповільніша
            if p := self.check_rozetka(): results.append({'source': 'Rozetka', 'price': p})

        except Exception as e:
            print(f"Global Error: {traceback.format_exc()}")
            return {'status': 'error', 'message': str(e), 'recommended': self.my_price}

        if not results:
            return {
                'status': 'no_data', 'min': 0, 'max': 0, 'recommended': self.my_price,
                'competitors': [], 'message': 'Товари не знайдено.'
            }

        prices = [x['price'] for x in results]
        min_p = min(prices)
        max_p = max(prices)

        floor_price = self.my_price * 0.85
        rec_price = max(min_p - 10, floor_price)

        return {
            'status': 'success',
            'competitors': results,
            'min': min_p,
            'max': max_p,
            'recommended': int(rec_price),
            'message': f"Знижено від лідера ({min_p})"
        }