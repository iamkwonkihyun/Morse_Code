import time
import asyncio
from functions.functions import get_morse_input, multiplay, clear_screen, print_ascii_art
from pynput import keyboard

selected = 0
options = ["practice morse code", "join server"]
prev_selected = -1

def on_press(key):
    """ 키 입력 감지 함수 """
    global selected, prev_selected

    if key == keyboard.Key.up:
        selected = (selected - 1) % len(options)
    elif key == keyboard.Key.down:
        selected = (selected + 1) % len(options)
    elif key == keyboard.Key.enter:
        return False  # 리스너 종료 (선택 완료)

    return True  # 계속 실행

def main_menu():
    """ 옵션 선택 메뉴 """
    global prev_selected

    with keyboard.Listener(on_press=on_press) as listener:
        while listener.running:
            if selected != prev_selected:
                clear_screen()
                print_ascii_art()
                for i, option in enumerate(options):
                    if i == selected:
                        print(f"{option:>32}   <--\n")  # 선택된 옵션 강조
                    else:
                        print(f"{option:>32}\n")
                prev_selected = selected

            time.sleep(0.1)  # 너무 빠른 반복 방지

    return options[selected]

if __name__ == "__main__":
    clear_screen()
    choice = main_menu()

    if choice == "practice morse code":
        get_morse_input()
    elif choice == "join server":
        # Mac nickname 입력 오류 변수
        nickName = input("nickName: ").strip()  # 아무런 역할 안함
        asyncio.run(multiplay())
