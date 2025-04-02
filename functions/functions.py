import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import sys
import time
import threading
import pygame
import json
import requests
import websockets
import logging
import asyncio
import keyboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="app.log",
    filemode="a"
)

# pygame 초기화
pygame.mixer.init()

# 데이터 불러오기
with open("data/morse_code.json", "r", encoding="utf-8") as f:
    morse_code_data = json.load(f)
with open("data/server_data.json", "r", encoding="utf-8") as f:
    server_data = json.load(f)

# 변수
morse_code = morse_code_data["MORSE_CODE"]["ENG_MORSE_CODE"]
morse_code_list = []
websocket = None
previous_people = None
exit_flag = False
nick_name = ""
beep_long = pygame.mixer.Sound("assets/beep_long.wav")
beep_short = pygame.mixer.Sound("assets/beep_short.wav")
last_time = time.time()

# 상수
REVERSE_MORSE = {value: key for key, value in morse_code.items()}


async def connect_server():
    """웹소켓 연결 전 기존 연결을 닫고 새 연결 생성"""
    global websocket

    if websocket and not websocket.closed:
        await websocket.close()  # 기존 연결 닫기

    try:
        websocket = await websockets.connect(server_data["WS_URI"])
        await websocket.send("not receiver")
        logging.info("WebSocket 연결됨!")
    except Exception as e:
        logging.error(f"웹소켓 연결 실패: {e}")
        await asyncio.sleep(5)  # 5초 후 재시도
        await connect_server()


async def keep_websocket_alive():
    """WebSocket 연결을 유지하기 위해 30초마다 ping 전송"""
    while not exit_flag:
        try:
            if websocket is not None and not websocket.closed:
                await websocket.send("ping")
            await asyncio.sleep(30)  # 30초마다 Ping 전송
        except Exception as e:
            await connect_server()  # 연결이 끊어졌으면 다시 연결


async def send_message(nickName, morseCode):
    """서버로 모스부호 보내는 함수"""
    await websocket.send(f"{nickName}: {morseCode}")
    await websocket.recv()


def print_eng_morse():
    """모스부호 표 출력 함수"""
    print("""
A : . -        | B : - . . .    | C : - . - .    | D : - . .
E : .          | F : . . - .    | G : - - .      | H : . . . .
I : . .        | J : . - - -    | K : - . -      | L : . - . . 
M : - -        | N : - .        | O : - - -      | P : . - - .
Q : - - . -    | R : . - .      | S : . . .      | T : -
U : . . -      | V : . . . -    | W : . - -      | X : - . . - 
Y : - . - -    | Z : - - . .    | 1 : . - - - -  | 2 : . . - - -
3 : . . . - -  | 4 : . . . . -  | 5 : . . . . .  | 6 : - . . . .
7 : - - . . .  | 8 : - - - . .  | 9 : - - - - .  | 0 : - - - - -
""")


def print_ascii_art():
    """아스키 아트 프린트 함수"""
    print("""
⢸⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⡇
⢸    ##   ##    ###    ######    #####   #######    ⡇
⢸    ### ###   ## ##   ##   ##  ##   ##   ##   #    ⡇
⢸    #######  ##   ##  ##   ##  ##        ##        ⡇
⢸    ## # ##  ##   ##  ######    #####    ####      ⡇
⢸    ##   ##  ##   ##  ## ##         ##   ##        ⡇
⢸    ##   ##   ## ##   ##  ###  ##   ##   ##   #    ⡇
⢸    ##   ##    ###    ##   ##   #####   #######    ⡇
⢸                                                   ⡇
⢸          ####     ###    #####    #######         ⡇
⢸         ##  ##   ## ##   ##  ##    ##   #         ⡇
⢸        ##       ##   ##  ##   ##   ##             ⡇
⢸        ##       ##   ##  ##   ##   ####           ⡇
⢸        ##       ##   ##  ##   ##   ##             ⡇
⢸         ##  ##   ## ##   ##  ##    ##   #         ⡇
⢸          ####     ###    #####    #######         ⡇
⢸⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⡇
                                                """)


def on_press_enter(key):
    """Enter 키 감지 함수"""
    global exit_flag, morse_code_list
    if key == keyboard.Key.enter:
        morse_code_list = []
        exit_flag = True


def on_press_esc(key):
    """Esc 키 감지 함수"""
    if key == keyboard.Key.esc:
        print("Bye Bye\n")
        os._exit(0)


def morseToText(morse_code, reverse_morse_dict=REVERSE_MORSE):
    """입력받은 모스부호를 영어로 변환

    Args:
        morse_code (dict): 모스부호
        reverse_morse_dict (dict): 키(모스부호):값(영어)

    Returns:
        입력받은 모스부호를 영어로 변환 후 리턴
    """
    words = morse_code.split('  ')  # 두 칸 띄어쓰기를 단어 구분자로 사용
    decoded_words = []
    for word in words:
        letters = word.split()  # 공백을 기준으로 글자 구분
        decoded_word = ''.join(reverse_morse_dict.get(letter, '?') for letter in letters)  # 모스부호를 문자로 변환
        decoded_words.append(decoded_word)
    return ' '.join(decoded_words) # 단어를 띄어쓰기로 연결하여 반환


def detect_enter():
    """enter 감지 함수"""
    global exit_flag, morse_code_list
    morse_code_list = []
    keyboard.wait("enter")
    exit_flag = True


def detect_esc():
    """esc 감지 함수"""
    keyboard.wait("esc")
    print("Bye Bye\n")
    os._exit(0)


def get_morse_input():
    """모스부호 입력 함수

    Returns:
        모스부호 딕셔너리: 입력받은 모스부호 딕셔너리
    """
    clear_screen()
    global exit_flag, morse_code_list
    exit_flag = False
    last_time = time.time()
    threading.Thread(target=detect_enter, daemon=True).start()
    threading.Thread(target=detect_esc, daemon=True).start()

    while not exit_flag:
        clear_screen()
        print_eng_morse()
        print("\n현재 입력된 모스부호:\n" + ''.join(morse_code_list))
        print("\n해석된 문자:\n" + morseToText(''.join(morse_code_list)))
        
        while not keyboard.is_pressed("space") and not keyboard.is_pressed("backspace"):
            if exit_flag:
                return ''.join(morse_code_list)
            time.sleep(0.01)

        if keyboard.is_pressed("backspace") and morse_code_list:
            morse_code_list.pop()
            clear_screen()
            print_eng_morse()
            print("\n현재 입력된 모스부호:\n" + ''.join(morse_code_list))
            print("\n해석된 문자:\n" + morseToText(''.join(morse_code_list)))
            time.sleep(0.1)
            continue
        
        press_time = time.time()
        beep_long.play(-1)

        while keyboard.is_pressed("space"):
            if exit_flag:
                beep_long.stop()
                return ''.join(morse_code_list)
            time.sleep(0.01)

        release_time = time.time()
        beep_long.stop()

        duration = release_time - press_time
        gap = press_time - last_time

        if gap > 0.7 and morse_code_list:
            morse_code_list.append('  ')
        elif gap > 0.3 and morse_code_list:
            morse_code_list.append(' ')

        if duration < 0.2:
            morse_code_list.append('.')
            beep_short.play()
        else:
            morse_code_list.append('-')

        last_time = release_time

    return ''.join(morse_code_list)


async def multiplay():
    """멀티플레이"""
    await connect_server()
    global nick_name
    
    while True:
        clear_screen()
        nick_name = input("nickName: ").strip()
        if len(nick_name) == 0 or nick_name == "":
            continue
        else:
            break
    while True:
        await send_message(nickName=nick_name, morseCode=morseToText(get_morse_input()))


def total_people():
    """동접자 받아오는 함수 (숫자만 깔끔하게 변경)"""
    global previous_people

    response = requests.get(server_data["TOTALPEOPLE_URL"])
    current_people = response.text.strip()  # 현재 접속자 수 가져오기

    if current_people != previous_people:
        sys.stdout.write("\r" + " " * 50 + "\r")  # 기존 출력 덮어쓰기 (잔여 글자 제거)
        sys.stdout.write(f"\ronline: {current_people}")  # 새로운 출력
        sys.stdout.flush()  # 즉시 반영
        previous_people = current_people  # 업데이트


def clear_screen():
    """옥시싹싹 함수"""
    os.system('cls' if os.name == 'nt' else 'clear')


async def websocket_listener():
    global online_count
    async with websockets.connect(server_data["WS_URI"]) as ws:
        await ws.send("receiver")  # 🚀 서버에게 "나는 receiver야"라고 알림

        sys.stdout.write("\033[2J")  # 화면 전체 지우기
        sys.stdout.write("\033[1;1Honline: 0   ")  # 1행 1열에 "online: 0" 고정
        sys.stdout.flush()

        while True:
            message = await ws.recv()

            if message.startswith("online:"):
                online_count = message.split(":")[1].strip()
                sys.stdout.write(f"\033[1;1Honline: {online_count}   ")  # 숫자 업데이트
                sys.stdout.flush()
            else:
                print(f"\n{message}")  # 웹소켓 메시지는 아래로 출력


async def periodic_total_people():
    """동접자 수를 주기적으로 확인하고 변동이 있을 때만 출력"""
    global previous_people

    while True:
        total_people()  # 접속자 확인 및 출력
        await asyncio.sleep(5)  # 5초마다 실행


async def two_func_start():
    """웹소켓과 동접자 확인을 동시에 실행"""
    clear_screen()
    
    # 웹소켓과 total_people 주기적 실행을 동시에 수행
    await asyncio.gather(
        periodic_total_people(),  # 동접자 확인 (변동 있을 때만 출력)
        websocket_listener()  # 웹소켓 실행
    )