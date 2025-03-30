import keyboard, time
from functions.functions import getMorseInput, joinServer, clearScreen

if __name__ == "__main__":
    options = ["practice morse code", "join server"]
    selected = 0
    prev_selected = -1  # 이전 선택 상태 저장

    while True:
        # 선택이 변경된 경우에만 화면 갱신
        if selected != prev_selected:
            clearScreen()
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
            for i, option in enumerate(options):
                if i == selected:
                    print(f"{option:>32}   <--\n")  # 선택된 옵션 강조
                else:
                    print(f"{option:>32}\n")
            prev_selected = selected

        # 키 이벤트 읽기
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "up":
                selected = (selected - 1) % len(options)
            elif event.name == "down":
                selected = (selected + 1) % len(options)
            elif event.name == "enter":
                break
                
        # 너무 빠른 반복으로 인한 중복 입력 방지를 위해 잠시 대기
        time.sleep(0.1)

    if options[selected] == "practice morse code":
        getMorseInput()
    elif options[selected] == "join server":
        joinServer()