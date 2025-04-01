import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import time, keyboard, os, threading, pygame, json, requests, websockets, logging
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정 (ERROR 이상만 기록)
    format="%(asctime)s - %(levelname)s - %(message)s",  # 로그 출력 형식
    datefmt="%Y-%m-%d %H:%M:%S",  # 시간 형식
    filename="app.log",  # 로그를 저장할 파일명
    filemode="a"  # 'a'는 기존 로그에 추가 (덮어쓰려면 'w')
)

# pygame 초기화
pygame.mixer.init()

# mainData.json 파일 불러오기
with open("data/mainData.json", "r", encoding="utf-8") as f:
    data = json.load(f)
morseCode = data["MORSE_CODE"]["ENG_MORSE_CODE"]

# 변수
morse = []
websocket = None
exit_flag = False
beep_long = pygame.mixer.Sound("assets/beep_long.wav")
beep_short = pygame.mixer.Sound("assets/beep_short.wav")

# 상수
REVERSE_MORSE = {value: key for key, value in morseCode.items()}
BASE_URL = "http://ec2-3-37-123-222.ap-northeast-2.compute.amazonaws.com:8000/"
WS_URL = "ws://ec2-3-37-123-222.ap-northeast-2.compute.amazonaws.com:8000/morse_code"
# BASE_URL = "ws://localhost:8000/"
ENDPOINT_MORSE_CODE = "morse_code"
ENDPOINT_TOTAL_PEOPLE = "total_people"


async def connect_server():
    """서버 연결 함수"""
    global websocket
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(WS_URL)
        logging.info("WebSocket 연결됨!")


async def send_message(nickName, morseCode):
    """서버로 모스코드 보내는 함수"""
    await websocket.send(f"{nickName}: {morseCode}")
    response = await websocket.recv()
    logging.info(response)


# 모스부호 출력 함수
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
                                                
    #     #   ####   ######     #####  ######   
    ##   ##  ######   ##  ##   ### ##   ##  ##  
    ### ###  ##  ##   ##  ##   ###      ##      
    #######  ##  ##   #####     ####    ####    
    ## # ##  ##  ##   ## ##       ###   ##      
    ##   ##  ######   ## ##    ## ###   ##  ##  
    ##   ##   ####   ### ###   #####   ######   
                                                
          ####    ####   #####    ######   
        ##  ##   ######   ## ##    ##  ##  
       ##   ##   ##  ##   ##  ##   ##      
       ##        ##  ##   ##  ##   ####    
       ##   ##   ##  ##   ##  ##   ##      
        ##  ##   ######   ## ##    ##  ##  
          ####    ####   #####    ######   
                                                """)


def detect_enter():
    """enter 감지 함수"""
    global exit_flag, morse
    morse = []
    keyboard.wait("enter")
    exit_flag = True


def detect_esc():
    """esc 감지 함수"""
    keyboard.wait("esc")
    print("Bye Bye\n")
    os._exit(0)


# 모스부호를 텍스트로 변환하는 함수
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
    return ' '.join(decoded_words)  # 단어를 띄어쓰기로 연결하여 반환


def get_morse_input():
    """모스부호 입력 함수

    Returns:
        모스부호 딕셔너리: 입력받은 모스부호 딕셔너리
    """
    clear_screen()
    global exit_flag, morse
    exit_flag = False
    last_time = time.time()
    threading.Thread(target=detect_enter, daemon=True).start()
    threading.Thread(target=detect_esc, daemon=True).start()

    while not exit_flag:
        clear_screen()
        print_eng_morse()
        print("\n현재 입력된 모스부호:\n" + ''.join(morse))
        print("\n해석된 문자:\n" + morseToText(''.join(morse)))
        
        while not keyboard.is_pressed("space") and not keyboard.is_pressed("backspace"):
            if exit_flag:
                return ''.join(morse)
            time.sleep(0.01)

        if keyboard.is_pressed("backspace") and morse:
            morse.pop()
            clear_screen()
            print_eng_morse()
            print("\n현재 입력된 모스부호:\n" + ''.join(morse))
            print("\n해석된 문자:\n" + morseToText(''.join(morse)))
            time.sleep(0.1)
            continue
        
        press_time = time.time()
        beep_long.play(-1)

        while keyboard.is_pressed("space"):
            if exit_flag:
                beep_long.stop()
                return ''.join(morse)
            time.sleep(0.01)

        release_time = time.time()
        beep_long.stop()

        duration = release_time - press_time
        gap = press_time - last_time

        if gap > 0.7 and morse:
            morse.append('  ')
        elif gap > 0.3 and morse:
            morse.append(' ')

        if duration < 0.2:
            morse.append('.')
            beep_short.play()
        else:
            morse.append('-')

        last_time = release_time

    return ''.join(morse)


async def multiplay():
    """멀티플레이"""
    await connect_server()

    while True:
        clear_screen()
        nickName = input("nickName: ").strip()
        if len(nickName) == 0 or nickName == "":
            continue
        else:
            break
    while True:
        morseCode = morseToText(get_morse_input())
        await send_message(nickName, morseCode)


def total_people():
    """동접자 받아오는 함수"""
    response = requests.get(urljoin(BASE_URL, ENDPOINT_TOTAL_PEOPLE))
    print(response.text)


def clear_screen():
    """옥시싹싹 함수"""
    os.system('cls' if os.name == 'nt' else 'clear')