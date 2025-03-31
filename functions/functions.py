import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import time, keyboard, os, threading, pygame, json, requests

# 초기화
pygame.mixer.init()

# mainData.json 파일 불러오기
with open("data/mainData.json", "r", encoding="utf-8") as f:
    data = json.load(f)
morseCode = data["MORSE_CODE"]["ENG_MORSE_CODE"]

# 변수
morse = []
exit_flag = False
beep_long = pygame.mixer.Sound("assets/beep_long.wav")
beep_short = pygame.mixer.Sound("assets/beep_short.wav")
reverse_morse_dict = {value: key for key, value in morseCode.items()}
url = "http://ec2-3-37-123-222.ap-northeast-2.compute.amazonaws.com:8000/morse"

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

# 모스부호 출력 함수
def printEngMorse():
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

# Enter 키 감지 함수
def detectEnter():
    global exit_flag, morse
    morse = []
    keyboard.wait("enter")
    exit_flag = True

# 모스부호를 텍스트로 변환하는 함수
def morseToText(morse_code, reverse_morse_dict=reverse_morse_dict):
    words = morse_code.split('  ')  # 두 칸 띄어쓰기를 단어 구분자로 사용
    decoded_words = []
    for word in words:
        letters = word.split()  # 공백을 기준으로 글자 구분
        decoded_word = ''.join(reverse_morse_dict.get(letter, '?') for letter in letters)  # 모스부호를 문자로 변환
        decoded_words.append(decoded_word)

    return ' '.join(decoded_words)  # 단어를 띄어쓰기로 연결하여 반환

def getMorseInput():
    clearScreen()
    global exit_flag, morse
    exit_flag = False
    last_time = time.time()
    threading.Thread(target=detectEnter, daemon=True).start()

    while not exit_flag:
        clearScreen()
        printEngMorse()
        print("\n현재 입력된 모스부호:\n" + ''.join(morse))
        print("\n해석된 문자:\n" + morseToText(''.join(morse)))
        
        while not keyboard.is_pressed("space") and not keyboard.is_pressed("backspace"):
            if exit_flag:
                return ''.join(morse)
            time.sleep(0.01)

        if keyboard.is_pressed("backspace") and morse:
            morse.pop()
            clearScreen()
            printEngMorse()
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

# p2p 시작 함수
def joinServer():
    while True:
        clearScreen()
        time.sleep(1)
        nickName = input("nickName: ").strip()
        if len(nickName) == 0 or nickName == "":
            continue
        else:
            break
    while True:
        morseCode = morseToText(getMorseInput())
        send_to_backend(nickName, morseCode)

# 백엔드로 모스부호 보내는 함수
def send_to_backend(nickName, morseCode):
    data = { "nickName" : nickName, "morseCode" : morseCode }
    try:
        response = requests.post(url=url, json=data)
        if response.status_code == 200:
            print("백엔드에 모스부호 전송 성공")
        else:
            print("백엔드 전송 실패:", response.status_code)
    except Exception as e:
        print("백엔드 연결 실패:", e)

def receive_thread():
    last_data = []  # 이전 데이터를 저장하는 리스트

    while True:
        response = requests.get(url)
        
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