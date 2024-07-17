import pygame
from pygame.locals import *
import sys
import tkinter
from tkinter import Tk, Canvas, SW
from dataclasses import dataclass, field
import random
import time

img_bg = pygame.image.load("fild_image3.jpg")

bg_y = 0


# ----------------------------------
#初期設定　定数
BOX_TOP_X = 0 # ゲーム領域の左上X座標
BOX_TOP_Y = 0 # ゲーム領域の左上Y座標
WALL_EAST = 800        # ゲーム領域の幅
WALL_SOUTH = 600       # ゲーム領域の高さ
BOX_CENTER = BOX_TOP_X + WALL_EAST /2 # ゲーム領域の中心

CANVAS_WIDTH = WALL_EAST    # Canvasの幅
CANVAS_HEIGHT = WALL_SOUTH  # Canvasの高さ
CANVAS_BACKGROUND = "lightgray"                      # Canvasの背景色

DURATION = 0.01        # 描画間隔


MESSAGE_Y = WALL_SOUTH / 2        # メッセージ表示のY座標

TROLLEY_X0 = WALL_EAST / 2 - 40   # トロッコ初期位置(x)
TROLLEY_Y0 = WALL_SOUTH - 150    # トロッコ初期位置(y)
TROLLEY_W = 100                  # トロッコの幅
TROLLEY_H = 125                  # トロッコ高さ
TROLLEY_IMAGE = tkinter.PhotoImage(file="torikko-oji.jpg")
TROLLEY_VX = (WALL_EAST / 2 - WALL_EAST / 6) # カーソル移動

IWA_WIDTH = 100                 # 岩の横幅
IWA_HEIGHT = 100               # 岩の長さ
IWA_VY = 5                    # 岩の落ちる速さ
IWA_IMAGE = tkinter.PhotoImage(file="iwa.jpg")          # 岩の色

ENADORI_BONUS = 50                # ボーナス点
ENADORI_WIDTH = 100               # ボーナスアイテムの幅
ENADORI_HEIGHT = 100              # ボーナスアイテムの高さ
ENADORI_VY = 4                    # ボーナスアイテムの落下速度
ENADORI_IMAGE = tkinter.PhotoImage(file="enadori.jpg")             # ボーナスアイテムの色

DROP_Y = [WALL_EAST / 2 - 40 - ENADORI_WIDTH, WALL_EAST / 6 - 40 - ENADORI_WIDTH,
          WALL_EAST * (5/6) - 40 - ENADORI_WIDTH]  #アイテムの出現する場所

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
        canvas.coords(self.id, self.x, self.y,
                      self.x + self.w, self.y + self.h)

    def move(self):                     # 移動させる
        self.x += self.vx
        self.y += self.vy

# Iwaは、MovingObjectを継承している。
class Iwa(MovingObject):
    def __init__(self, id, x, y, w, h, vy, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, vy)

#enadoriは、MovingObjectを継承している。
class Enadori(MovingObject):
    def __init__(self, id, x, y, w, h, vy, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, vy)

# Trolleyは、MovingObjectを継承している。
class Trolley(MovingObject):
    def __init__(self, id, x, y, w, h, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, 0)
        self.c = c

    def move(self):                     # トロッコだけ独自の移動
        self.x += self.vx
        if self.x < WALL_EAST / 6 - 40:
            self.x = WALL_EAST / 6 - 40
        if self.x > WALL_EAST * (5/6) - 40:
            self.x = WALL_EAST * (5/6) - 40
        self.vx = 0  #矢印キーを押した一瞬だけ反応
    
    def set_v(self, v):
        self.vx = v     # 移動量の設定は、独自メソッド

    def stop(self):     # 停止も、Paddle独自のメソッド
        self.vx = 0


# ----------------------------------
# Box(ゲーム領域)の定義
@dataclass
class Box:
    west: int
    north: int
    east: int
    south: int
    balls: list
    trolley: Trolley
    paddle_v: int
    blocks: list
    duration: float
    run: int
    score: int
    paddle_count: int
    iwa: Iwa                                #障害物(岩)のやつ
    enadori: Enadori                        #ポーナスアイテム（エナドリ）のやつ

    def __init__(self, x, y, w, h, duration):
        self.west, self.north = (x, y)
        self.east, self.south = (x + w, y + h)
        self.balls = []
        self.paddle = None
        self.blocks = []
        self.paddle_v = TROLLEY_VX
        self.duration = duration
        self.run = False
        self.score = 0  # 得点
        self.iwa = None
        self.enadori = None

    # トロッコの生成
    def create_trolley(self, x, y, w=TROLLEY_W, h=TROLLEY_H, c=TROLLEY_IMAGE):
        id = canvas.create_rectangle(x, y, x + w, y + h, image=c, tag="trolley_image")
        return Trolley(id, x, y, w, h, c)
    
    #岩の生成
    def create_iwa(self, x, y, w=IWA_WIDTH, h=IWA_HEIGHT, c=IWA_IMAGE):
        id = canvas.create_rectangle(x, y, x + w, y + h, image=c, tag="iwa_image")
        return Iwa(id, x, y, w, h, IWA_VY, c)

     # ボーナスアイテムの生成
    def create_enadori(self, x, y, w=ENADORI_WIDTH, h=ENADORI_HEIGHT, c=ENADORI_IMAGE):
        id = canvas.create_rectangle(x, y, x + w, y + h, image=c, tag="enadori_image")
        return Enadori(id, x, y, w, h, ENADORI_VY, c)

    def check_iwa(self, iwa, trolley):
        if (trolley.x <= iwa.x <= trolley.x + trolley.w \
            and iwa.y + iwa.h > trolley.y \
            and iwa.y <= trolley.y + trolley.h):  # 岩に当たった
            return True
        else:
            return False

    def check_candy(self, enadori, trolley):
        if (trolley.x <= enadori.x <= trolley.x + trolley.w \
            and enadori.y + enadori.h > trolley.y \
            and enadori.y <= trolley.y + trolley.h):  # ボーナスゲット！
            return True
        else:
            return False

    def left_trolley(self, event):   # トロッコを左に移動(Event処理)
        self.trolley.set_v(- self.trolley_v)

    def right_trolley(self, event):  # トロッコを右に移動(Event処理)
        self.trolley.set_v(self.trolley_v)

    def stop_trolley(self, event):   # トロッコを止める(Event処理)
        self.trolley.stop()

    def game_start(self, event):
        self.run = True

    def game_end(self, message):
        self.run = False
        canvas.create_text(BOX_CENTER, MESSAGE_Y,
                           text=message, font=('FixedSys', 16))
        tk.update()

    def update_score(self):
        canvas.itemconfigure(self.id_score,
                             text="score:" + str(self.score))

    def wait_start(self):
        # SPACEの入力待ち
        id_text = canvas.create_text(BOX_CENTER, MESSAGE_Y,
                                     text="Press 'SPACE' to start",
                                     font=('FixedSys', 16))
        tk.update()
        while not self.run:    # ひたすらSPACEを待つ
            tk.update()
            time.sleep(self.duration)
        canvas.delete(id_text)  # SPACE入力のメッセージを削除
        tk.update()

    def set(self):   # 初期設定を一括して行う
        # スコアの表示
        self.id_score = canvas.create_text(
                BOX_TOP_X,
                BOX_TOP_Y - 2,
                text=("score: " + str(self.score)),
                font=("FixedSys", 16), justify="left",
                anchor=SW
                )

        # トロッコの生成
        self.trolley = self.create_trolley(TROLLEY_X0, TROLLEY_Y0,TROLLEY_W, TROLLEY_H, TROLLEY_IMAGE)
        # イベント処理の登録
        canvas.bind_all('<KeyPress-Right>', self.right_trolley)
        canvas.bind_all('<KeyPress-Left>', self.left_trolley)
        #canvas.bind_all('<KeyRelease-Right>', self.stop_paddle)
        #canvas.bind_all('<KeyRelease-Left>', self.stop_paddle)
        canvas.bind_all('<KeyPress-space>', self.game_start)  # SPACEが押された
        
    def animate(self):
        # 動くものを一括登録
        self.movingObjs = [self.trolley]
        while self.run:
            for obj in self.movingObjs:
                obj.move()          # 座標を移動させる
            
            for obj in self.movingObjs:
                obj.redraw()    # 移動後の座標で再描画(画面反映)
            time.sleep(self.duration)
            tk.update()






# -------------------
tk=Tk()
tk.title("Game")

canvas = Canvas(tk, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_BACKGROUND)
canvas.pack()

# ----------------------------------
# メインルーチン
box = Box(BOX_TOP_X, BOX_TOP_Y, WALL_EAST, WALL_SOUTH, DURATION)
box.set()           # ゲームの初期設定
box.wait_start()    # 開始待ち
box.animate()       # アニメーション

