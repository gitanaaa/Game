# Python によるプログラミング：第 8 章
# 前半のまとめ ( ブロック崩し )
# --------------------------
# プログラム名: ex08-blocks.py

from tkinter import Tk, Canvas, SW
from dataclasses import dataclass, field
import random
import time
from tkinter import PhotoImage

# =================================================
# -------------------
tk=Tk()
tk.title("Game")

#------------------------------
# 初期設定値(定数)
BOX_TOP_X = 0 # ゲーム領域の左上X座標
BOX_TOP_Y = 0 # ゲーム領域の左上Y座標
WALL_EAST = 800        # ゲーム領域の幅
WALL_SOUTH = 600       # ゲーム領域の高さ
BOX_CENTER = BOX_TOP_X + WALL_EAST /2 # ゲーム領域の中心

CANVAS_WIDTH = WALL_EAST    # Canvasの幅
CANVAS_HEIGHT = WALL_SOUTH  # Canvasの高さ
CANVAS_BACKGROUND = "lightgray"                      # Canvasの背景色

TITLE_BACK_X = 150          #タイトル背景の四角形のX座標
TITLE_BACK_Y = 0            #タイトル背景の四角形のY座標
TITLE_BACK_WIDTH = 650      #タイトル背景の四角形の幅
TITLE_BACK_HIGHT = 600      #タイトル背景の四角形の高さ
TITLE_BACK_LINE = 1         #タイトル背景の四角形の枠線の長さ

DURATION = 0.01       # 描画間隔


MESSAGE_Y = WALL_SOUTH / 2        # メッセージ表示のY座標

TROLLEY_X0 = WALL_EAST / 2 - 52   # トロッコ初期位置(x)
TROLLEY_Y0 = WALL_SOUTH - 150    # トロッコ初期位置(y)
TROLLEY_W = 80                  # トロッコの幅
TROLLEY_H = 120                  # トロッコ高さ
TROLLEY_VX = (WALL_EAST / 2 - WALL_EAST / 4.5) - 17 # トロッコ移動

DRINK_BONUS = 50                # ボーナス点
DRINK_WIDTH = 20                # ボーナスアイテムの幅
DRINK_HEIGHT = 20               # ボーナスアイテムの高さ
DRINK_COLOR = "red"

ROCK_WIDTH = 20                # 岩アイテムの幅
ROCK_HEIGHT = 20               # 岩アイテムの高さ
ROCK_COLOR = "red"

DROP_SPEED = 5                  #アイテムの落ちる速度
DROP_X = [TROLLEY_X0 ,TROLLEY_X0 - TROLLEY_VX,
          TROLLEY_X0 + TROLLEY_VX]  #アイテムの出現する場所X軸
DROP_Y = 0 - DRINK_WIDTH      #アイテムの出現する場所X軸
ANCHOR = "nw"                  #アイテムの表示座標の基準


# ----------------------------------
# 共通の親クラスとして、MovingObjectを定義
@dataclass
class MovingObject:
    id: int
    x: int
    y: int
    w: int
    h: int
    vx: int
    vy: int

    def redraw(self):                   # 再描画(移動結果の画面反映)
        canvas.coords(self.id, self.x, self.y)

    def move(self):                     # 移動させる
        self.x += self.vx
        self.y += self.vy

class Drink(MovingObject):
    def __init__(self, id, x, y, w, h, vy, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, vy)
        

class Rock(MovingObject):
    def __init__(self, id, x, y, w, h, vy, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, vy)



# Trolleyは、MovingObjectを継承している。
class Trolley(MovingObject):
    def __init__(self, id, x, y, w, h, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, 0)
        self.c = c

    def move(self):                     # トロッコだけ独自の移動
        self.x += self.vx
        if self.x < TROLLEY_X0 - TROLLEY_VX:
            self.x = TROLLEY_X0 - TROLLEY_VX
        if self.x > TROLLEY_X0 + TROLLEY_VX:
            self.x = TROLLEY_X0 + TROLLEY_VX
        self.vx = 0  #矢印キーを押した一瞬だけ反応
    
    def set_v(self, v):
        self.vx = v     # 移動量の設定は、独自メソッド

    def stop(self):     # 停止も、Paddle独自のメソッド
        self.vx = 0

#----------------------------------
#画像ファイルのパス設定
TROLLEY = "torikko-oji2.png"
IWA = "iwa2.png"
DRINK = "enadori2.png"
BACK = "fild_image3-1(png).png"

#インスタンスと紐づけ
trolley_img = PhotoImage(file=TROLLEY)
iwa_img = PhotoImage(file=IWA)
drink_img = PhotoImage(file=DRINK)
back_img = PhotoImage(file=BACK)
# ----------------------------------
# Box(ゲーム領域)の定義
@dataclass
class Box:
    west: int
    north: int
    east: int
    south: int
    title_select: int
    start_ruletext: int
    trolley: Trolley
    trolley_v: int
    drinks:list
    rocks:list
    socre:int
    duration: float
    run: int

    def __init__(self, x, y, w, h, duration):
        self.west, self.north = (x, y)
        self.east, self.south = (x + w, y + h)
        self.title_select = 1
        self.start_ruletext = 2
        self.trolley_v = TROLLEY_VX
        self.drinks = []
        self.rocks = []
        self.score = 0
        self.duration = duration
        self.run = False



    #タイトル画面選択肢の表示(カーソルが合えば文字がピンク色になる)
    def start_text_color(self, title_select):
        global start
        if self.title_select == 1:
            start = canvas.create_text(BOX_CENTER, MESSAGE_Y+20,
                                     text="START",
                                     fill = "magenta",
                                     font=('Snap ITC', 25))
            return start
        else:
            start = canvas.create_text(BOX_CENTER, MESSAGE_Y+20,
                                     text="START",
                                     font=('Snap ITC', 25))
            return start
            
    def rule_text_color(self, title_select):
        global rule
        if self.title_select == 0:
            rule = canvas.create_text(BOX_CENTER, MESSAGE_Y + 80,
                                     text="RULE",
                                     fill = "magenta",
                                     font=('Snap ITC', 25))
            return rule
        else:
            rule = canvas.create_text(BOX_CENTER, MESSAGE_Y + 80,
                                     text="RULE",                               
                                     font=('Snap ITC', 25))
            return rule
        
    #ルール説明
    def rule_text(self):
        self.rule_text = canvas.create_text(BOX_CENTER, MESSAGE_Y - 60,
                                     text="～ ルール ～",
                                     font=('Malgun Gothic',30))
        self.rule_text1 = canvas.create_text(TITLE_BACK_X + 25, MESSAGE_Y,
                                     text="①：方向キーの右と左を使って移動しよう",
                                     anchor = "nw",
                                     font=('Malgun Gothic',16))
        self.rule_text2 = canvas.create_text(TITLE_BACK_X + 25, MESSAGE_Y + 50,
                                     text="②：岩をよけて行動しよう",
                                     anchor = "nw",
                                     font=('Malgun Gothic',16))
        self.rule_text3 = canvas.create_text(TITLE_BACK_X + 25, MESSAGE_Y + 100,
                                     text="③：ボーナスアイテムをとって得点を稼ごう",
                                     anchor = "nw",
                                     font=('Malgun Gothic',16))
        self.rule_text4 = canvas.create_text(TITLE_BACK_X + 400, MESSAGE_Y + 170,
                                     text="～以上～",
                                     font=('Malgun Gothic',18))
        self.rule_text5 = canvas.create_text(TITLE_BACK_X + 440, MESSAGE_Y + 200,
                                     text="ふぁいと～",
                                     font=('Malgun Gothic',10))
        self.rule_text6 = canvas.create_text(TITLE_BACK_X + 400, 550,
                                     text="'Press Enter' To Title",
                                     font=('Malgun Gothic',14))
        tk.update()

    def rule_text_delete(self):
        canvas.delete(self.rule_text, self.rule_text1, self.rule_text2, self.rule_text3, self.rule_text4,
                      self.rule_text5, self.rule_text6)
        tk.update()
        del self.rule_text
        del self.rule_text1
        del self.rule_text2
        del self.rule_text3
        del self.rule_text4
        del self.rule_text5
        del self.rule_text6
        
        
    # トロッコの生成
    def create_paddle(self, x, y, w, h, c):
        id = canvas.create_image(TROLLEY_X0, TROLLEY_Y0,
                                 image = trolley_img,
                                 anchor = ANCHOR)
        return Trolley(id, x, y, w, h, c)

    # ドリンクの生成
    def create_drink(self, x, y, w=DRINK_WIDTH, h=DRINK_HEIGHT, c=DRINK_COLOR):
        id = canvas.create_image(random.choice(DROP_X), DROP_Y,
                                 image = drink_img,
                                 anchor = ANCHOR)
        return Drink(id, x, y, w, h, DROP_SPEED, c)

    #岩の生成
    def create_rock(self, x, y, w=ROCK_WIDTH, h=ROCK_HEIGHT, c=ROCK_COLOR):
        id = canvas.create_image(random.choice(DROP_X), DROP_Y,
                                 image = iwa_img,
                                 anchor = ANCHOR)
        return Drink(id, x, y, w, h, DROP_SPEED, c)

    #アイテムが下にそれたときの処理
    #ドリンク
    def check_wall_drink(self, drink):
        if drink.y + drink.h >= self.south:  # 下に逃した
            return True
        return False

    #岩
    def check_wall_rock(self, rock):
        if rock.y + rock.h >= self.south:  # 下に逃した
            return True
        return False


    #ドリンクがトロッコに当たったときの処理
    def check_drink(self, drink, trolley):
        if (trolley.x == drink.x \
            and drink.y + drink.h > trolley.y \
            and drink.y <= trolley.y + trolley.h):
            return True
        else:
            return False

    #岩がトロッコに当たったときの処理
    def check_rock(self, rock, trolley):
        if (trolley.x == rockk.x \
            and rock.y + rock.h > trolley.y \
            and rock.y <= trolley.y + trolley.h):
            return True
        else:
            return False
        

    #タイトル画面キー操作
    def start_text_select(self, event):
        self.title_select = 1

    def rule_text_select(self, event):
        self.title_select = 0

    def game_start(self, event):
        if self.title_select == 1 and self.start_ruletext % 2 == 0:
            self.run = True
        else:
            self.start_ruletext += 1

    
    def left_trolley(self, event):   # トロッコを左に移動(Event処理)
        self.trolley.set_v(- self.trolley_v)

    def right_trolley(self, event):  # トロッコを右に移動(Event処理)
        self.trolley.set_v(self.trolley_v)

    def stop_trolley(self, event):   # トロッコを止める(Event処理)
        self.trolley.stop()

    def game_end(self, message):
        self.run = False
        canvas.create_text(BOX_CENTER, MESSAGE_Y,
                           text=message, font=('FixedSys', 16))
        tk.update()


    def title(self):
        #タイトル画面のイベントハンドラ
        canvas.bind_all('<KeyPress-Down>', self.rule_text_select)
        canvas.bind_all('<KeyPress-Up>', self.start_text_select)
        canvas.bind_all('<Key-space>', self.game_start)  # SPACEが押された

        #背後の四角形
        canvas.create_rectangle(TITLE_BACK_X, TITLE_BACK_Y, TITLE_BACK_WIDTH, TITLE_BACK_HIGHT,
                                fill = "wheat",
                                width = TITLE_BACK_LINE)

        #タイトル名
        id_text = canvas.create_text(BOX_CENTER, MESSAGE_Y-200,
                                     text="Trolley",
                                     font=('Jokerman',20))
        id_text2 = canvas.create_text(BOX_CENTER, MESSAGE_Y-150,
                                     text="ADVENTURE",
                                     font=('Ravie', 40))
        
        #タイトル画面（ルール画面もあり）
        while not self.run:    # スタートボタンが押されるまで待つ
            if self.start_ruletext % 2 == 0:           #タイトル画面
                self.start_text_color(self.title_select)
                self.rule_text_color(self.title_select)
                tk.update()
                time.sleep(self.duration)
                tk.update()
                canvas.delete(start)
                canvas.delete(rule)

            else:                                       #ルール説明画面
                self.rule_text()
                while self.start_ruletext % 2 == 1:
                    tk.update()
                    time.sleep(self.duration)
                self.rule_text_delete()                
                    
            #print(self.title_select)
            #time.sleep(self.duration)
            #canvas.delete(id_text)
        canvas.delete("all")
        tk.update()

        
        

    def set(self):   # 初期設定を一括して行う
        
        canvas.create_image(0, 0, image = back_img, anchor = "nw")

        # スコアの表示
        self.id_score = canvas.create_text(
            BOX_TOP_X + 40,
            BOX_TOP_Y + 40,
            text=("score: " + str(self.score)),
            font=("Malgun Gothic", 20), justify="left",
            fill="red",
            anchor=SW
            )
        
        # トロッコの生成
        self.trolley = self.create_paddle(TROLLEY_X0, TROLLEY_Y0,
                                         TROLLEY_W, TROLLEY_H,
                                         "red")

        # イベント処理の登録
        canvas.bind_all('<KeyPress-Right>', self.right_trolley)
        canvas.bind_all('<KeyPress-Left>', self.left_trolley)
        #canvas.bind_all('<KeyRelease-Right>', self.stop_paddle)
        #canvas.bind_all('<KeyRelease-Left>', self.stop_paddle)
        

    def animate(self):
        # 動くものを一括登録
        self.movingObjs = [self.trolley]
        while self.run:
            for obj in self.movingObjs:
                obj.move()          # 座標を移動させる

            for drink in self.drinks:
                if self.check_wall_drink(drink):   #下にそらした時の処理(ドリンク)
                    canvas.delete(drink.id)
                    self.drinks.remove(drink)
                    self.movingObjs.remove(drink)
            for rock in self.rocks:
                if self.check_wall_rock(rock):   #下にそらした時の処理(ドリンク)
                    canvas.delete(rock.id)
                    self.rocks.remove(rock)
                    self.movingObjs.remove(rock)
            if random.random() < 0.01:  #ドリンクが確率1%で発生
                drink = self.create_drink(random.choice(DROP_X), DROP_Y)
                self.drinks.append(drink)
                self.movingObjs.append(drink)
            if random.random() < 0.005:  #岩が確率0.5%で発生
                rock = self.create_rock(random.choice(DROP_X), DROP_Y)
                self.rocks.append(rock)
                self.movingObjs.append(rock)

            
            for obj in self.movingObjs:
                obj.redraw()    # 移動後の座標で再描画(画面反映)
            time.sleep(self.duration)
            tk.update()

#------------------------------------------------------------------------------
canvas = Canvas(tk, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_BACKGROUND)
canvas.pack()
# ----------------------------------
# メインルーチン
box = Box(BOX_TOP_X, BOX_TOP_Y, WALL_EAST, WALL_SOUTH, DURATION)
box.title()         # タイトル画面 
box.set()           # ゲームの初期設定
box.animate()       # アニメーション
