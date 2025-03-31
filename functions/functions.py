import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import time, keyboard, os, threading, pygame, json, requests, websockets, logging, sys
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정 (ERROR 이상만 기록)
    format="%(asctime)s - %(levelname)s - %(message)s",  # 로그 출력 형식
    datefmt="%Y-%m-%d %H:%M:%S",  # 시간 형식
    filename="app.log",  # 로그를 저장할 파일명
    filemode="a"  # 'a'는 기존 로그에 추가 (덮어쓰려면 'w')
)

# 초기화
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
# base_url = "ws://ec2-3-37-123-222.ap-northeast-2.compute.amazonaws.com:8000/"
BASE_URL = "ws://localhost:8000/"
ENDPOINT_MORSE_CODE = "morse_code"
ENDPOINT_TOTAL_PEOPLE = "total_people"


async def connect_server():
    global websocket
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(urljoin(BASE_URL, ENDPOINT_MORSE_CODE))
        logging.info("✅ WebSocket 연결됨!")

async def send_message(nickName, morseCode):
    await websocket.send(f"{nickName}: {morseCode}")
    response = await websocket.recv()
    logging.info(response)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# 모스부호 출력 함수
def print_eng_morse():
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

# Enter 키 감지 함수
def detect_enter():
    global exit_flag, morse
    morse = []
    keyboard.wait("enter")
    exit_flag = True


def detect_esc():
    keyboard.wait("esc")
    print("Bye Bye\n")
    os._exit(0)

# 모스부호를 텍스트로 변환하는 함수
def morseToText(morse_code, reverse_morse_dict=REVERSE_MORSE):
    words = morse_code.split('  ')  # 두 칸 띄어쓰기를 단어 구분자로 사용
    decoded_words = []
    for word in words:
        letters = word.split()  # 공백을 기준으로 글자 구분
        decoded_word = ''.join(reverse_morse_dict.get(letter, '?') for letter in letters)  # 모스부호를 문자로 변환
        decoded_words.append(decoded_word)
    return ' '.join(decoded_words)  # 단어를 띄어쓰기로 연결하여 반환


def get_morse_input():
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


async def join_server():
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



def receive_morse_code():
    last_data = []  # 이전 데이터를 저장하는 리스트

    while True:
        response = requests.get(BASE_URL)
        
        try:
            data = response.json()  # JSON 형식으로 응답을 파싱
        except ValueError:
            print("응답이 JSON 형식이 아닙니다.")
            return

        # 응답 데이터에서 'data' 키를 꺼내기
        if "data" in data:
            data = data["data"]  # 'data' 안에 있는 리스트만 추출

            # 새로운 데이터 찾기 (last_data에 없던 것만 출력)
            new_entries = [entry for entry in data if entry not in last_data]

            if new_entries:
                for entry in new_entries:
                    # entry가 문자열이라면, ':'로 split하여 nickName과 morseCode 추출
                    if isinstance(entry, str):  
                        parts = entry.split(" : ")
                        if len(parts) == 2:
                            nickName, morseCode = parts
                            print(f"{nickName} : {morseCode}")
                    
                # 마지막으로 본 데이터를 갱신
                last_data.extend(new_entries)

        time.sleep(1)  # 1초마다 GET 요청


def total_people():
    response = requests.get(urljoin(BASE_URL, ENDPOINT_TOTAL_PEOPLE))
    print(response.text)