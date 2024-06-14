import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from async_sql_scripts import *
from async_markdownv2 import *
from text_scripts import *
from selen_xvfb import *
from webscraping_funcs import *
from config import *


bot = AsyncTeleBot(telegram_token)


@bot.message_handler(commands=['start'])
async def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        chat_type = message.chat.type
        if chat_type == 'private':
            if not await check_user_exists(user_id):
                try:
                    await add_user_to_db(user_id, username)
                except Exception as error:
                    print(f"Error adding user to db error:\n{error}")
            else:
                await update_username(user_id, username)

            verified_status = await get_verified_status(user_id)

            if verified_status == 0:
                text = await escape(dictionary['start_msg_not_verified'].format(username), flag=0)
                button_list1 = [
                    types.InlineKeyboardButton("Get permission", callback_data="get_perm"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

            elif verified_status == 1:
                text = await escape(dictionary['start_msg_under_review'].format(username), flag=0)
                button_list1 = [
                    types.InlineKeyboardButton("Please, wait", callback_data="please_wait"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

            elif verified_status == 2:
                text = await escape(dictionary['start_msg_under_review'].format(username), flag=0)
                button_list1 = [
                    types.InlineKeyboardButton("Available commands", callback_data="commands"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

            elif verified_status == 3:
                text = await escape(dictionary['start_msg_under_review'].format(username), flag=0)
                button_list1 = [
                    types.InlineKeyboardButton("Available commands", callback_data="commands"),
                ]
                reply_markup = types.InlineKeyboardMarkup([button_list1])
                await bot.send_message(message.chat.id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")

            await change_menu_status(user_id, start_menu_status)

    except Exception as e:
        print(f"Error in start message: {e}")


@bot.message_handler(commands=['verified'])
async def verified(message):
    try:
        user_id = message.from_user.id

        chat_type = message.chat.type
        if chat_type == 'private':
            if user_id == admin_id:
                list_of_verified_users = await get_all_verified_users()

                text_output = "⭐️ **Verified Users** ⭐️\n\n"
                for user in list_of_verified_users:
                    text_output += f"- @{user}\n"

                text = await escape(text_output, flag=0)
                await bot.send_message(message.chat.id, text=text, parse_mode="MarkdownV2")

    except Exception as error:
        print(error)


@bot.message_handler(commands=['revoke'])
async def revoke(message):
    try:
        user_id = message.from_user.id

        chat_type = message.chat.type
        if chat_type == 'private':
            if user_id == admin_id:

                user_name = (message.text).split(" ")[1]

                await change_verified_username_status(user_name, 0)

                text_output = dictionary['revoked_username'].format(user_name)

                text = await escape(text_output, flag=0)
                await bot.send_message(message.chat.id, text=text, parse_mode="MarkdownV2")

    except Exception as error:
        print(error)


@bot.message_handler(commands=['promote'])
async def promote(message):
    try:
        user_id = message.from_user.id

        chat_type = message.chat.type
        if chat_type == 'private':
            if user_id == admin_id:

                user_name = (message.text).split(" ")[1]

                await change_verified_username_status(user_name, 2)

                text_output = dictionary['promoted_username'].format(user_name)

                text = await escape(text_output, flag=0)
                await bot.send_message(message.chat.id, text=text, parse_mode="MarkdownV2")

    except Exception as error:
        print(error)


@bot.message_handler(commands=['notif'])
async def notif(message):
    try:
        user_id = message.from_user.id

        chat_type = message.chat.type
        if chat_type == 'private':
            if user_id == admin_id:

                notif_text = (message.text).split(" ")[1:]
                text_output = " ".join(notif_text)

                text = await escape(text_output, flag=0)
                user_list = await get_all_users()

                for user_id in user_list:
                    try:
                        await bot.send_message(user_id, text=text, parse_mode="MarkdownV2")
                    except:
                        pass

    except Exception as error:
        print(error)


@bot.message_handler(commands=['wallet_scan'])
async def wallet_scan(message):
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        chat_type = message.chat.type
        if chat_type == 'private':
            channel_member = await bot.get_chat_member(channel_id, user_id)
            if channel_member.status in ["creator", "administrator", "member"]:
                verified_status = await get_verified_status(user_id)

                if verified_status == 2:
                    if not await check_user_exists(user_id):
                        try:
                            await add_user_to_db(user_id, username)
                        except Exception as error:
                            print(f"Error adding user to db error:\n{error}")
                    else:
                        await update_username(user_id, username)
                    try:
                        wallet_address = (message.text).split(" ")[1]

                        # wallet_check = await check_wallet_address(wallet_address)
                        wallet_check = True

                        coins = []
                        if wallet_check == True:
                            await bot.send_message(chat_id=user_id, text=await escape(dictionary['request_processing'], flag=0), parse_mode="MarkdownV2")

                            trade_daily_results, trade_weekly_results, trade_monthly_results, realized_pnl_value_daily, realized_pnl_value_weekly, realized_pnl_value_monthly, winrate_value_monthly, tokens_traded_value_monthly, tags, wallet_balance = await get_trade_wallet_data_from_cielo(wallet_address)

                            trd_rslts = [trade_daily_results, trade_weekly_results, trade_monthly_results]

                            counter = 1
                            for trade_results_list in trd_rslts:
                                for result in trade_results_list:

                                    emoji = "1️⃣"
                                    if counter == 1:
                                        emoji = "1️⃣**st** Trade ⬇️"
                                    elif counter == 2:
                                        emoji = "2️⃣**nd** Trade⬇️"
                                    elif counter == 3:
                                        emoji = "3️⃣**rd** Trade ⬇️"
                                    elif counter == 4:
                                        emoji = "4️⃣**th** Trade ⬇️"
                                    elif counter == 5:
                                        emoji = "5️⃣**th** Trade ⬇️"
                                    coin = (f"{emoji}\n"
                                            f"🪙**Coin:** `{result['coin_name']}`\n"
                                            f"💸**Realized PNL:** `{result['pnl_price']} / {result['pnl_percent']}`\n"
                                            f"🟢**Bought:** `{result['bought_value']}`\n"
                                            f"🔴**Sold:** `{result['sold_value']}`")
                                    if len(coins) < 5:
                                        coins.append(coin)

                                    if len(coins) >= 5:
                                        break

                                    counter += 1

                            if len(tags) > 0:
                                tags_text = ", ".join(tags)
                                text_form = (f"💳**Wallet:** `{wallet_address}`\n\n"
                                             f"💰**Balance:** `{wallet_balance}`\n\n"
                                             f"🔅**Tags:** **{tags_text}**\n\n"
                                             f"🎗**Winrate:** `{winrate_value_monthly}`\n"
                                             f"👁‍🗨**Tokens Traded:** `{tokens_traded_value_monthly}`\n\n"
                                             f"📈**Daily PNL:** `{realized_pnl_value_daily}`\n"
                                             f"📈**Weekly PNL:** `{realized_pnl_value_weekly}`\n"
                                             f"📈**Monthly PNL:** `{realized_pnl_value_monthly}`\n\n"
                                             f"📊**Last 5 Trades:**\n\n")
                            else:
                                text_form = (f"💳**Wallet:** `{wallet_address}`\n\n"
                                             f"💰**Balance:** `{wallet_balance}`\n\n"
                                             f"🎗**Winrate:** `{winrate_value_monthly}%`\n"
                                             f"👁‍🗨**Tokens Traded:** `{tokens_traded_value_monthly}`\n\n"
                                             f"📈**Daily PNL:** `{realized_pnl_value_daily}`\n"
                                             f"📈**Weekly PNL:** `{realized_pnl_value_weekly}`\n"
                                             f"📈**Monthly PNL:** `{realized_pnl_value_monthly}`\n\n"
                                             f"📊**Last 5 Trades:**\n\n")
                            if len(coins) > 0:
                                last_5_trades = "\n\n".join(coins)
                            else:
                                last_5_trades = "**This wallet has not traded for a long time.**"

                            text = await escape(text_form + last_5_trades, flag=0)
                            await bot.send_message(chat_id=user_id, text=text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                        else:
                            await bot.send_message(chat_id=user_id, text=await escape(dictionary['wrong_address'], flag=0), parse_mode="MarkdownV2")
                    except Exception as error:
                        print(error)
                        await bot.send_message(chat_id=user_id, text=await escape(dictionary['wrong_address'], flag=0), parse_mode="MarkdownV2")
                else:
                    await bot.send_message(chat_id=user_id, text=await escape(dictionary['not_verified'], flag=0), parse_mode="MarkdownV2")
            else:
                await bot.send_message(chat_id=user_id, text=await escape(dictionary['need_to_sub'], flag=0), parse_mode="MarkdownV2")
    except Exception as error:
        print("Error in wallet_scan func")
        print(error)


@bot.message_handler(commands=['contract_scan'])
async def contract_scan(message):
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        chat_type = message.chat.type
        if chat_type == 'private':
            channel_member = await bot.get_chat_member(channel_id, user_id)
            if channel_member.status in ["creator", "administrator", "member"]:
                verified_status = await get_verified_status(user_id)

                if verified_status == 2:
                    if not await check_user_exists(user_id):
                        try:
                            await add_user_to_db(user_id, username)
                        except Exception as error:
                            print(f"Error adding user to db error:\n{error}")
                    else:
                        await update_username(user_id, username)
                    try:
                        contract_address = (message.text).split(" ")[1]
                        contract_check = await contract_address_check(contract_address)

                        if contract_check == True:
                            await bot.send_message(chat_id=user_id, text=await escape(dictionary['request_processing'], flag=0), parse_mode="MarkdownV2")

                            risk_title, risk_value, risk_status, risk_alerts, overview_data, holders_data, hrefs, market_data = await get_contract_address_info(contract_address)

                            output = ""

                            # overview_data
                            if overview_data:
                                output += "🔸 **Token Overview** 🔸\n"
                                for key, value in overview_data.items():
                                    if key == "Mint":
                                        output += f"**{key}:** [{value}]({hrefs[0]})\n"
                                    elif key == "Mint Authority":
                                        output += f"**{key}:** [{value}]({hrefs[1]})\n"
                                    else:
                                        output += f"**{key}:** `{value}`\n"
                            else:
                                output += "🔸 **Token Overview** 🔸\n"

                            # risk alerts
                            if risk_title and risk_value and risk_status:
                                output += "\n🔺 **Risk Analysis** 🔻\n"
                                output += f"⚠️ **Value:** `{risk_value}`\n"
                                output += f"🗯 **Status:** `{risk_status}`\n"
                                output += "📢 **Alerts:**\n"
                                for alert in risk_alerts:
                                    output += f" - `{alert}`\n"
                            else:
                                output += "\n🔺 **Risk Analysis** 🔻"

                            # holders_data
                            if holders_data:
                                output += "\n📊 **Top Holders** 📊\n"
                                for holder in holders_data:
                                    output += f"👤**Account: {holder['account']}, ⚡️ Amount: `{holder['amount']}`, ➗ Percentage: `{holder['percentage']}`**\n"
                            else:
                                output += ""

                            if len(market_data) > 0:
                                output += "\n📝 **Markets** 📝\n"
                                for item in market_data:
                                    pairs = "{} / {}".format(item['Pairs'][0], item['Pairs'][1])
                                    market_liq = item['Liquidity']
                                    market_lp_locked = item['LP Locked']

                                    output += (f"⚖️ **Pair:** `{pairs}`\n"
                                               f"💸 **Liquidity:** `{market_liq}`\n"
                                               f"🔒 **LP Locked:** `{market_lp_locked}`\n"
                                               f"---------------------------------\n")

                            else:
                                output += ""

                            text = await escape(output, flag=0)
                            await bot.send_message(chat_id=user_id, text=text, parse_mode="MarkdownV2", disable_web_page_preview=True)
                        else:
                            await bot.send_message(chat_id=user_id, text=await escape(dictionary['wrong_ca'], flag=0), parse_mode="MarkdownV2")
                    except Exception as error:
                        print(error)
                        await bot.send_message(chat_id=user_id, text=await escape(dictionary['wrong_ca'], flag=0), parse_mode="MarkdownV2")
                else:
                    await bot.send_message(chat_id=user_id, text=await escape(dictionary['not_verified'], flag=0), parse_mode="MarkdownV2")
            else:
                await bot.send_message(chat_id=user_id, text=await escape(dictionary['need_to_sub'], flag=0), parse_mode="MarkdownV2")
    except Exception as error:
        print("Error in contract_scan func")
        print(error)


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    user_id = call.message.chat.id
    username = call.from_user.username

    if call.data == "get_perm":
        verified_status = await get_verified_status(user_id)
        if verified_status == 0:
            await change_verified_status(user_id, 1)
            await bot.answer_callback_query(call.id, text="Your request has been sent successfully.", show_alert=True)

            text = await escape(dictionary["user_request"].format(username), flag=0)
            button_list1 = [
                types.InlineKeyboardButton("Approve 👍", callback_data=f"approve_{user_id}"),
                types.InlineKeyboardButton("Ignore 👎", callback_data=f"ignore_{user_id}"),
            ]
            reply_markup = types.InlineKeyboardMarkup([button_list1])

            await bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup, parse_mode="MarkdownV2")
        else:
            await bot.answer_callback_query(call.id, text="You have already sent a request.", show_alert=True)

    elif call.data == "please_wait":
        await bot.answer_callback_query(call.id, text="You have already sent a request.", show_alert=True)

    elif call.data == "commands":
        await bot.send_message(chat_id=admin_id, text=await escape(dictionary['start_msg_verified'], flag=0), parse_mode="MarkdownV2")

    elif call.data.startswith("approve_"):
        await bot.answer_callback_query(call.id, text="You have approved the application.", show_alert=True)
        user_id = int(call.data.split("_")[1])

        await change_verified_status(user_id, 2)
        await bot.send_message(chat_id=user_id, text=await escape(dictionary['app_accepted'], flag=0), parse_mode="MarkdownV2")

    elif call.data.startswith("ignore_"):
        await bot.answer_callback_query(call.id, text="You have rejected application.", show_alert=True)
        user_id = int(call.data.split("_")[1])
        await change_verified_status(user_id, 3)


async def contract_address_check(contract_address):
    if 30 < len(contract_address) < 50:
        return True
    return False


async def check_wallet_address(wallet_address):
    return True
    # async def is_valid_ethereum_address(address):
    #     pattern = re.compile(r"^0x[a-fA-F0-9]{40}$")
    #     return bool(pattern.match(address))
    #
    # async def is_valid_solana_address(address):
    #     pattern = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
    #     return bool(pattern.match(address))
    # 
    # evm_wallet = await is_valid_ethereum_address(wallet_address)
    # sol_wallet = await is_valid_solana_address(wallet_address)
    #
    # if evm_wallet == True or sol_wallet == True:
    #     return True
    # return False


async def get_contract_address_info(contract_address):
    html = await rugcheck_scrap(contract_address)
    return await parse_rugcheck(html)


async def get_trade_wallet_data_from_cielo(wallet_address):
    html_daily, html_weekly, html_monthly = await cielo_scrap(wallet_address)
    trade_daily_results, realized_pnl_value_daily, winrate_value_daily, tokens_traded_value_daily, tags, wallet_balance = await parse_cielo(html_daily)
    trade_weekly_results, realized_pnl_value_weekly, winrate_value_weekly, tokens_traded_value_weekly, tags, wallet_balance = await parse_cielo(html_weekly)
    trade_monthly_results, realized_pnl_value_monthly, winrate_value_monthly, tokens_traded_value_monthly, tags, wallet_balance = await parse_cielo(html_monthly)
    return trade_daily_results, trade_weekly_results, trade_monthly_results, realized_pnl_value_daily, realized_pnl_value_weekly, realized_pnl_value_monthly, winrate_value_monthly, tokens_traded_value_monthly, tags, wallet_balance


async def run_services():
    try:
        bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=500))
        await asyncio.gather(bot_task)
    except Exception as error:
        print(error)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_services())
    loop.run_forever()
