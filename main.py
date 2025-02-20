import tkinter as tk

def get_user_choices():
    def submit():
        # 선택한 값 저장
        global is_process, is_plot
        is_process = process_var.get()
        is_plot = plot_var.get()
        root.destroy()  # 창 닫기

    # GUI 창 생성
    root = tk.Tk()
    root.title("모드 선택")
    root.geometry("350x250")  # 창 크기 확대

    # 폰트 크기 설정
    label_font = ("Arial", 12, "bold")
    button_font = ("Arial", 12)

    # 질문 1: 데이터를 처리할 것인가?
    process_var = tk.BooleanVar(value=False)
    process_label = tk.Label(root, text="Do you want to process the raw data?", font=label_font)
    process_label.pack(pady=(10, 5))
    process_frame = tk.Frame(root)  # 버튼을 그룹핑
    process_yes = tk.Radiobutton(process_frame, text="Yes", variable=process_var, value=True, font=button_font)
    process_no = tk.Radiobutton(process_frame, text="No", variable=process_var, value=False, font=button_font)
    process_yes.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
    process_no.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
    process_frame.pack()

    # 질문 2: 데이터를 플롯할 것인가?
    plot_var = tk.BooleanVar(value=False)
    plot_label = tk.Label(root, text="Do you want to plot the processed data?", font=label_font)
    plot_label.pack(pady=(10, 5))
    plot_frame = tk.Frame(root)  # 버튼을 그룹핑
    plot_yes = tk.Radiobutton(plot_frame, text="Yes", variable=plot_var, value=True, font=button_font)
    plot_no = tk.Radiobutton(plot_frame, text="No", variable=plot_var, value=False, font=button_font)
    plot_yes.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
    plot_no.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
    plot_frame.pack()

    # 확인 버튼 (크기 키우기)
    submit_button = tk.Button(root, text="Submit", command=submit, font=button_font, padx=20, pady=10)
    submit_button.pack(pady=15, ipadx=15, ipady=5)  # 내부 여백 추가

    root.mainloop()

    return is_process, is_plot

# 사용자 선택 받기
is_process, is_plot = get_user_choices()

# 선택 결과 출력
print("Process Data:", is_process)  # True 또는 False 반환
print("Plot Data:", is_plot)  # True 또는 False 반환
