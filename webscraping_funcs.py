import asyncio
import re
from bs4 import BeautifulSoup


async def parse_cielo(html):
    realized_pnl_value = "$0.00"
    winrate_value = "0"
    tokens_traded_value = "0"
    tags = []
    try:
        soup = BeautifulSoup(html, 'html.parser')

        blocks = soup.find_all('div', {'data-index': True, 'data-known-size': True, 'data-item-index': True})

        results = []


        for block in blocks:
            try:
                coin_name_div = block.find('div', class_='text-14 text-textBase')
                coin_name = coin_name_div.text.strip() if coin_name_div else 'N/A'

                pnl_div = block.find('div', class_='flex flex-col gap-1')

                try:
                    pnl_price_div = pnl_div.find('div', class_='text-green text-14')
                    pnl_price = pnl_price_div.text.strip()
                except:
                    pnl_price_div = pnl_div.find('div', class_='text-red text-14')
                    pnl_price = pnl_price_div.text.strip()


                pnl_percent_div = pnl_div.find('div', class_='text-textSecondary text-14 font-semibold') if pnl_div else None
                pnl_percent = pnl_percent_div.text.strip() if pnl_percent_div else 'N/A'

                transactions = block.find_all('div', class_='flex gap-1')

                if len(transactions) >= 2:
                    bought_value_divs = transactions[1].find('div', class_='text-green text-14')
                    bought_value = bought_value_divs.text.strip() if bought_value_divs else 'N/A'

                    sold_value_divs = transactions[2].find('div', class_='text-red text-14')
                    sold_value = sold_value_divs.text.strip() if sold_value_divs else 'N/A'
                else:
                    bought_value = sold_value = 'N/A'

                results.append({
                    'coin_name': coin_name,
                    'pnl_price': pnl_price,
                    'pnl_percent': pnl_percent,
                    'bought_value': bought_value,
                    'sold_value': sold_value,
                })
            except AttributeError:
                continue

        realized_pnl_blocks = soup.find_all('div', class_='flex flex-col gap-2 min-w-[80px]')
        for realized_pnl_block in realized_pnl_blocks:
            try:
                try:
                    realized_pnl_value = realized_pnl_block.find('div', class_='text-14 font-bold text-green').text.strip()
                    realized_pnl_value = realized_pnl_value.split()[0]
                except:
                    try:
                        realized_pnl_value = realized_pnl_block.find('div', class_='text-14 font-bold text-textBase').text.strip()
                        realized_pnl_value = realized_pnl_value.split()[0]
                    except:
                        realized_pnl_value = realized_pnl_block.find('div', class_='text-14 font-bold text-red').text.strip()
                        realized_pnl_value = realized_pnl_value.split()[0]
            except AttributeError:
                continue
        try:
            winrate_blocks = soup.find_all('div', class_='flex flex-col gap-2 min-w-[80px]')
            winrate_value = winrate_blocks[2].text
            winrate_value = re.findall(r'\d+\.?\d*', winrate_value)
            winrate_value = [float(num) if '.' in num else int(num) for num in winrate_value][0]
        except:
            winrate_value = "0"
        try:
            tokens_traded_blocks = soup.find_all('div', class_='flex flex-col gap-2 min-w-[80px]')
            tokens_traded_value = tokens_traded_blocks[3].text
            tokens_traded_value = re.findall(r'\d+\.?\d*', tokens_traded_value)
            tokens_traded_value = [float(num) if '.' in num else int(num) for num in tokens_traded_value][0]
        except:
            tokens_traded_value = "0"
        try:
            tags_block = soup.find_all('div', class_='flex gap-1 items-start')
            tag_elements = tags_block[0].find_all('p', class_='text-14 text-textBase')
            tags = [tag.text.strip().rstrip(',') for tag in tag_elements]
        except:
            tags = []
    except Exception as error:
        print(error)
        results = [{'coin_name': "N/A",
                    'pnl_price': "N/A",
                    'pnl_percent': "N/A",
                    'bought_price': "N/A",
                    'bought_value': "N/A",
                    'sold_price': "N/A",
                    'sold_value': "N/A"}]
    return results, realized_pnl_value, winrate_value, tokens_traded_value, tags


async def parse_rugcheck(html):
    risk_title = risk_value = risk_status = "N/A"
    risk_alerts = holders_data = ['N/A']
    overview_data = {}
    hrefs = ['https://solana.fm/', 'https://solana.fm/']
    market_data = []
    try:
        soup = BeautifulSoup(html, "html.parser")

        risk_title = risk_value = risk_status = None
        risk_alerts = []
        overview_data = {}
        holders_data = []

        risk_analysis_card = soup.find('div', class_='card')
        if risk_analysis_card and 'Risk Analysis' in risk_analysis_card.text:
            risk_header = risk_analysis_card.find('div', class_='card-header')
            risk_body = risk_analysis_card.find('div', class_='card-body')

            if risk_header:
                risk_title = risk_header.find('h4').text.strip() if risk_header.find('h4') else None
                risk_value = risk_header.find('small').text.strip() if risk_header.find('small') else None

            if risk_body:
                risk_status = risk_body.find('h1', class_='mb-0 lg').text.strip() if risk_body.find('h1', class_='mb-0 lg') else None

                alert_rows = risk_body.find_all('div', class_='alert')
                for row in alert_rows:
                    alert_text = row.text.strip()
                    risk_alerts.append(alert_text)


        token_body = soup.find_all('tbody')
        if token_body:
            rows = token_body[0].find_all('tr')
            hrefs = [a['href'] for a in token_body[0].find_all('a', href=True)]
            overview_data = {}
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value_tag = cols[1].find('a') or cols[1].find('span') or cols[1].find('code') or cols[1]
                    value = value_tag.text.strip()
                    overview_data[key] = value


        table = soup.find('table', {'data-v-2083cb03': True})
        holders_data = []

        if table:
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 3:
                    account = cols[0].text.strip()
                    href_link = cols[0].find('a', href=True)['href']
                    account = f"[{account}]({href_link})"
                    amount = cols[1].text.strip()
                    percentage = cols[2].text.strip()
                    holders_data.append({
                        'account': account,
                        'amount': amount,
                        'percentage': percentage
                    })

        market_table = soup.find('table', {'data-v-5b9159a6': True})
        market_rows = market_table.find_all('tr')[1:]

        for row in market_rows:
            columns = row.find_all('td')
            if columns:
                try:
                    # market_img = columns[0].find('img')['src'] if columns[0].find('img') else None
                    # address_link = columns[1].find('a')['href'] if columns[1].find('a') else None
                    # pair_links = [a['href'] for a in columns[2].find_all('a')]
                    pairs = columns[2].get_text().split('/')
                    pairs = [pair.strip() for pair in pairs]
                    # lp_mint_link = columns[3].find('a')['href'] if columns[3].find('a') else None
                    market_liquidity = columns[4].text.strip()
                    market_lp_locked = columns[5].text.strip()

                    market_data.append({
                        # 'Market Image': market_img,
                        # 'Address URL': address_link,
                        # 'Pair URLs': pair_links,
                        'Pairs': pairs,
                        # 'LP Mint URL': lp_mint_link,
                        'Liquidity': market_liquidity,
                        'LP Locked': market_lp_locked
                    })
                except:
                    pass


        return risk_title, risk_value, risk_status, risk_alerts, overview_data, holders_data, hrefs, market_data
    except Exception as error:
        print(error)
        return risk_title, risk_value, risk_status, risk_alerts, overview_data, holders_data, hrefs, market_data


# with open('html.txt', 'r', encoding='utf-8') as file:
#     html = file.read()
#
# asyncio.run(parse_rugcheck(html))
