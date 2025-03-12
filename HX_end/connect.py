import socket
import sys,os
def p(P):
    print(P);
def cmd(S="pause"):
    os.system(S);
client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_s.connect(("192.168.0.100", 8501))
def SCWR(S=""):
    client_s.send(S.encode("utf-8"))
    recv_content = client_s.recv(1024) 
    return recv_content.decode("utf-8")
def SR(S1):
    return SCWR(f"RDS {S1} 1\r\n").strip("\r\n");
def SW(S1,S2):
    return SCWR(f"WRS {S1} 1 {S2}\r\n").strip("\r\n");
import tkinter as tk
import time
root = tk.Tk()
#root.iconbitmap('mfc.ico')
root.geometry('450x450+100+100')
root.resizable(0,0)
root.title("")
def gettime():
    dstr.set(time.strftime("%H:%M:%S"))
    root.after(1000, gettime)# 每隔 1s 调用一次
dstr = tk.StringVar()# 定义动态字符串
lb = tk.Label(root,textvariable=dstr,fg='green',font=("微软雅黑",20))
lb.pack()
gettime()
def click_button():
    R=SR("R90100")
    p(R)
    p(type(R))
    if R=="0":
        SW("R90100",1)
    if R=="1":
        SW("R90100",0)
button = tk.Button(root,text='小',bg='#7CCD7C',width=20, height=5,command=click_button)
button.config(bg='#808080');#button1.config(bg='#ff0000')
def click_button1():
    R=SR("R90300")
    p(R)
    p(type(R))
    if R=="0":
        SW("R90300",1)
    if R=="1":
        SW("R90300",0)
button1 = tk.Button(root,text='大',bg='#7CCD7C',width=20, height=5,command=click_button1)
button1.config(bg='#808080');#button1.config(bg='#ff0000')
def getpgnum():# 获取
    global button1
    global button
    R1=SR("R51208")
    R2=SR("R51008")
    R3=SR("R90300")
    R4=SR("R90100")
    if R3=="0":
        button1.config(bg='#ff0000')
    if R3=="1":
        button1.config(bg='#808080');  
    if R4=="0":
        button.config(bg='#ff0000')
    if R4=="1":
        button.config(bg='#808080');       
    dstr00.set(f"{R1}{R2}{R3}{R4}")
    root.after(80, getpgnum)    #调用一次
dstr00 = tk.StringVar()
lb111 = tk.Label(root,textvariable=dstr00,fg='green',font=("微软雅黑",10))# 
lb111.pack()#place(x=0, y=40)
getpgnum()# 调用
button1.pack()
button.pack()
root.mainloop()
client_s.close()
cmd()