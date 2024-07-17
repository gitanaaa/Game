# Python によるプログラミング：第 8 章
# 前半のまとめ ( ブロック崩し )
# --------------------------
# プログラム名: ex08-blocks.py

from tkinter import Tk, Canvas, SW
from dataclasses import dataclass, field
import random
import time

# =================================================
# 初期設定値(定数)
BOX_TOP_X = 0 # ゲーム領域の左上X座標
BOX_TOP_Y = 0 # ゲーム領域の左上Y座標
WALL_EAST = 700        # ゲーム領域の幅
WALL_SOUTH = 500       # ゲーム領域の高さ
BOX_CENTER = BOX_TOP_X + WALL_EAST /2 # ゲーム領域の中心

CANVAS_WIDTH = WALL_EAST    # Canvasの幅
CANVAS_HEIGHT = WALL_SOUTH  # Canvasの高さ
CANVAS_BACKGROUND = "lightgray"                      # Canvasの背景色

DURATION = 0.01        # 描画間隔


MESSAGE_Y = WALL_SOUTH / 2        # メッセージ表示のY座標

TROLLEY_X0 = WALL_EAST / 2 - 40   # トロッコ初期位置(x)
TROLLEY_Y0 = WALL_SOUTH - 150    # トロッコ初期位置(y)
TROLLEY_W = 80                  # トロッコの幅
TROLLEY_H = 120                  # トロッコ高さ
TROLLEY_VX = (WALL_EAST / 2 - WALL_EAST / 6) # カーソル移動



DRINK_WIDTH = 20                # エナドリの横幅
DRINK_HEIGHT = 20               # エナドリの長さ
DRINK_COLOR = "blue"            # エナドリの色

CANDY_BONUS = 50                # ボーナス点
CANDY_WIDTH = 20                # ボーナスアイテムの幅
CANDY_HEIGHT = 20               # ボーナスアイテムの高さ
CANDY_COLOR = "RED"             # ボーナスアイテムの色

ROCK_WIDTH = 20                # 岩アイテムの幅
ROCK_HEIGHT = 20               # 岩アイテムの高さ
ROCK_COLOR = "RED"             # 岩アイテムの色

DROP_SPEED = 5                  #アイテムの落ちる速度
DROP_Y = [WALL_EAST / 2 - 40 - DRINK_WIDTH, WALL_EAST / 6 - 40 - DRINK_WIDTH,
          WALL_EAST * (5/6) - 40 - DRINK_WIDTH]  #アイテムの出現する場所

ADD_SCORE = 10                  # 得点の増加値

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



# 各アイテムはは、MovingObjectを継承している。
class Drink(MovingObject):
    def __init__(self, id, x, y, w, h, vy, c):
        MovingObject.__init__(self, id, x, y, w, h, 0, vy)


class Candy(MovingObject):
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
    trolley_v: int
    blocks: list
    duration: float
    run: int
    score: int
    paddle_count: int
    #spear: Spear
    #candy: Candy

    def __init__(self, x, y, w, h, duration):
        self.west, self.north = (x, y)
        self.east, self.south = (x + w, y + h)
        self.balls = []
        self.paddle = None
        self.blocks = []
        self.trolley_v = TROLLEY_VX
        self.duration = duration
        self.run = False
        self.score = 0  # 得点
        self.paddle_count = 0    # パドルでボールを打った回数
        #self.spear = None
        #self.candy = None


    # トロッコの生成
    def create_paddle(self, x, y, w, h, c):
        id = canvas.create_rectangle(x, y, x + w, y + h, fill=c,)
        return Trolley(id, x, y, w, h, c)

    # スピードアップドリンクの生成
    def create_spear(self, x, y, w=DRINK_WIDTH, h=DRINK_HEIGHT, c=DRINK_COLOR):
        id = canvas.create_rectangle(x, y, x + w, y + h, fill=c)
        return Drink(id, x, y, w, h, DROP_SPEED, c)

   

    def check_wall(self, ball):   # 壁に当たった時の処理
        if ball.y + ball.d + ball.vy >= self.south:  # 下に逃した
            return True
        if (ball.x + ball.vx <= self.west \
            or ball.x + ball.d + ball.vx >= self.east):
            ball.vx = -ball.vx
        if ball.y + ball.vy <= self.north:
            ball.vy = -ball.vy
        return False

    def check_paddle(self, paddle, ball):  # ボールがパドルに当たった処理
        hit = False
        # 左から当たる
        if (paddle.x <= ball.x + ball.d + ball.vx <= paddle.x + paddle.w
            and paddle.y <= ball.y + ball.d/2 + ball.vy <= paddle.y + paddle.h):
            hit = True
            ball.vx = - ball.vx
        # 上から当たる
        elif (paddle.y <= ball.y + ball.d + ball.vy <= paddle.y + paddle.h
            and paddle.x <= ball.x + ball.d/2 + ball.vx <= paddle.x + paddle.w):
            # ボールの位置によって、反射角度を変える
            hit = True
            ball.vx = int(6*(ball.x + ball.d/2 - paddle.x) / paddle.w) - 3
            ball.vy = - ball.vy
        # 右から当たる
        elif (paddle.x <= ball.x + ball.vx <= paddle.x + paddle.w \
            and paddle.y <= ball.y + ball.d/2 + ball.vy <= paddle.y + paddle.h):
            hit = True
            ball.vx = - ball.vx
        # パドルのボーダーチェック
        if paddle.x + paddle.vx <= self.west:
            paddle.stop()
            paddle.x = self.west
        elif self.east <= paddle.x + paddle.vx + paddle.w:
            paddle.stop()
            paddle.x = self.east - paddle.w
        if hit: # パドルにボールが当たった
            self.paddle_count += 1
            if self.paddle_count % MULTI_BALL_COUNT == 0: # ボールを発生
                if len(self.balls) < BALL_MAX_NUM:
                    ball = self.create_ball(BALL_X0, BALL_Y0,
                                            BALL_DIAMETER,
                                            random.choice(VX0), BALL_VY)
                    self.balls.append(ball)
                    self.movingObjs.append(ball)
            if self.paddle_count % PADDLE_SHORTEN_COUNT == 0: # パドルを短くするか？
                if paddle.w > PADDLE_MIN_W:  # まだ短くできる！
                    paddle.w -= PADDLE_SHORTEN
            if self.paddle_count % SPEED_UP == 0: # ボールを加速させるか？
                if ball.vy > -BALL_MAX_VY: # まだ加速できる！
                    ball.vy -= 1   # ボールが上向きになっていることに注意！

    def check_block(self, block, ball):  # ボールがブロックに当たったか判定
        # 上から当たる
        if (block.y <= ball.y + ball.d + ball.vy <= block.y + block.h \
            and block.x <= ball.x + ball.d/2 + ball.vx <= block.x + block.w):
            ball.vy = - ball.vy
            return True
        # 右から当たる
        elif (block.x <= ball.x + ball.vx <= block.x + block.w
            and block.y <= ball.y + ball.d/2 + ball.vy <= block.y + block.h):
            ball.vx = - ball.vx
            return True
        # 左から当たる
        elif (block.x <= ball.x + ball.d + ball.vx <= block.x + block.w
            and block.y <= ball.y + ball.d/2 + ball.vy <= block.y + block.h):
            ball.vx = - ball.vx
            return True
        # 下から当たる
        elif (block.y <= ball.y + ball.vy <= block.y + block.h
            and block.x <= ball.x + ball.d/2 + ball.vx <= block.x + block.w):
            ball.vy = - ball.vy
            return True
        else:
            return False

    def check_spear(self, spear, paddle):
        if (paddle.x <= spear.x <= paddle.x + paddle.w \
            and spear.y + spear.h > paddle.y \
            and spear.y <= paddle.y + paddle.h):  # 槍に当たった
            return True
        else:
            return False

    def check_candy(self, candy, paddle):
        if (paddle.x <= candy.x <= paddle.x + paddle.w \
            and candy.y + candy.h > paddle.y \
            and candy.y <= paddle.y + paddle.h):  # ボーナスゲット！
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
        self.trolley = self.create_paddle(TROLLEY_X0, TROLLEY_Y0,
                                         TROLLEY_W, TROLLEY_H,
                                         "red")

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
