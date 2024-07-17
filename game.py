import tkinter
from PIL import ImageTk, Image

WALL_EAST = 800        # ゲーム領域の幅
WALL_SOUTH = 600       # ゲーム領域の高さ
CANVAS_WIDTH = WALL_EAST    # Canvasの幅
CANVAS_HEIGHT = WALL_SOUTH  # Canvasの高さ




y = 300
y2 = -300
y3 = 900
trolley_x = 400
trolley_y = 525
iwa_x = 400
iwa_y = 0
enadori_x = 200
enadori_y = 50
collision = False
key = ""
iwa_life = False

def key_down(e):
    global key
    global trolley_x
    global collision
    key = e.keysym
    if collision == False:
        if key == "Left":
            trolley_x = trolley_x - 200
            if trolley_x < 200:
                trolley_x = 200
        if key == "Right":
            trolley_x = trolley_x + 200
            if trolley_x > 600:
                trolley_x = 600

def key_up(e):
    global key
    key = ""



def scroll():
    global y
    global y2
    global y3
    global trolley_x
    global trolley_y
    global iwa_y
    global iwa_y
    global collision
    global iwa_life
    global enadori_x
    global enadori_y

    #if iwa_life == False:
    #    iwa_x = random.randint(2,6)*100
    #    iwa_y = 100
    #    iwa_life = True
    #if trolley_y-70<=iwa_y+50<=trolley_y+70 and iwa_x-50<=trolley_x+50 and trolley_x-50<=iwa_x+50:
    #    collision = True
    #    y = y
    #    y2 = y2
    #    y3 = y3
    #    trolley_x = trolley_x
    #    trolley_y = trolley_y
    #    iwa_x = iwa_x
    #    iwa_y = iwa_y
    #else:
    if y2 == 900:
        y2 = y - 600
    if y == 900:
        y = y3 - 600
    if y3 == 900:
        y3 = y2 -600
    y = y + 10
    y2 = y2 + 10
    y3 = y3 + 10
    iwa_y = iwa_y + 10
    enadori_y = enadori_y + 10
    canvas.coords("HAIKEI1",400,y)
    canvas.coords("HAIKEI2",400,y-600)
    canvas.coords("HAIKEI3",400,y+600)
    canvas.coords("TROLLEY",trolley_x,525)
    canvas.coords("IWA",iwa_x,iwa_y)
    canvas.coords("ENADORI",200,iwa_y)
    #if iwa_y >= 550:
    #    iwa_life = False
    tk.after(100,scroll)



# -------------------
tk = tkinter.Tk()
tk.title("Game")
tk.bind("<KeyPress>",key_down)
tk.bind("<KeyRelease>",key_up)
canvas = tkinter.Canvas(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
canvas.pack()
image1 = Image.open("fild_image3-1.jpg")
bgimage = ImageTk.PhotoImage(image1, master=tk)
canvas.create_image(400,y,image=bgimage,tag="HAIKEI1")
canvas.create_image(400,y2,image=bgimage,tag="HAIKEI2")
canvas.create_image(400,y3,image=bgimage,tag="HAIKEI3")
image2 = Image.open("torikko-oji2.png")
trolleyimage = ImageTk.PhotoImage(image2, master=tk)
canvas.create_image(400,525,image=trolleyimage,tag="TROLLEY")
image3 = Image.open("iwa2.png")
iwaimage = ImageTk.PhotoImage(image3, master=tk)
canvas.create_image(iwa_x,iwa_y,image=iwaimage,tag="IWA")
image4 = Image.open("enadori2.png")
enadoriimage = ImageTk.PhotoImage(image4, master=tk)
canvas.create_image(200,50,image=enadoriimage,tag="ENADORI")





# ----------------------------------
# メインルーチン
#box = Box(BOX_TOP_X, BOX_TOP_Y, WALL_EAST, WALL_SOUTH, DURATION)
#box.set()           # ゲームの初期設定
scroll()
#box.wait_start()    # 開始待ち
#box.animate()       # アニメーション
tk.mainloop()

