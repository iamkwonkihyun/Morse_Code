import asyncio
import threading
from functions.functions import detect_esc, two_func_start

if __name__ == "__main__":
    threading.Thread(target=detect_esc, daemon=True).start()
    asyncio.run(two_func_start())
