import pygame
import random
from pygame.locals import *
from itertools import cycle
import sys

SCREENWIDTH = 822  # 窗口宽度
SCREENHEIGHT = 199  # 窗口高度
FPS = 30  # 窗口更新画面的时间

# 游戏结束
def game_over():
    bump_audio = pygame.mixer.Sound('audio/bump.wav')       # 撞击音效
    bump_audio.play()       # 播放撞击音效
    # 获取窗体的高、宽
    screen_w = pygame.display.Info().current_w
    screen_h = pygame.display.Info().current_h
    # 加载游戏结束的照片
    over_img = pygame.image.load('image/gameover.png').convert_alpha()
    # 图片绘制在窗口中间位置
    SCREEN.blit(over_img, ((screen_w - over_img.get_width()) / 2, (screen_h - over_img.get_height()) / 2))


def mainGame():
    score = 0  # 得分
    over = False
    global SCREEN, FPSCLOCK
    pygame.init()  # pygame初始化
    # 创建clock对象，控制每个循环多长时间执行一次
    FPSCLOCK = pygame.time.Clock()
    # 创建窗体，进行程序交互
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    # 设置当前窗口标题
    pygame.display.set_caption('玛丽冒险')
    # 创建地图对象
    bg1 = MyMap(0, 0)
    bg2 = MyMap(800, 0)

    # 创建玛丽对象
    marie = Marie()
    # 创建障碍物信息
    addObstaleTimer = 0  # 添加障碍物的时间
    obstacle_list = []  # 障碍物对象列表
    # 创建背景音乐按钮
    music_button = Music_Button()
    btn_img = music_button.open_img
    # 循环播放
    music_button.bg_music.play(-1)

    # 检查窗体的显示与刷新
    while True:
        # 获取单机事件，需要循环检查发生的每个事件
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()  # 退出窗口
                sys.exit()  # 关闭窗口
            # 判断是否按下了空格
            if event.type == KEYDOWN and event.key == K_SPACE:
                if marie.rect.y >= marie.lowest_y:  # 如果玛丽在地面上
                    marie.jump_audio.play()  # 播放跳跃音效
                    marie.jump()  # 开启跳跃状态
                # 判断游戏是否结束，结束后按空格键重新开始游戏
                if over:
                    mainGame()
            # 判断鼠标事件
            if event.type == pygame.MOUSEBUTTONUP:
                if music_button.is_select():
                    # 修改播放状态
                    if music_button.is_open:
                        # 关闭播放状态
                        music_button.is_open = False
                        # 关闭后显示关闭状态的图片
                        btn_img = music_button.close_img
                        # 停止播放
                        music_button.bg_music.stop()
                    else:
                        # 相反操作
                        music_button.is_open = True
                        btn_img = music_button.open_img
                        music_button.bg_music.play(-1)

        # 实现地图循环滚动
        if not over:
            # 绘制地图，贴到幕布上
            bg1.map_update()
            # 地图移动
            bg1.map_rolling()
            # 后半个图片贴入，移动
            bg2.map_update()
            bg2.map_rolling()

            # 玛丽移动
            marie.move()
            # 绘制玛丽
            marie.draw_marie()

            # 计算障碍物出现的时间，添加障碍物
            if addObstaleTimer > 1300:
                r = random.randint(0, 100)
                if r > 40:
                    # 创建障碍物
                    obstacle = Obstacle()
                    # 添加障碍物到列表中去
                    obstacle_list.append(obstacle)
                # 重置添加时间
                addObstaleTimer = 0
            # 遍历障碍物列表，绘制障碍物
            for i in range(len(obstacle_list)):
                obstacle_list[i].obstacle_move()
                obstacle_list[i].draw_obstacle()
                # 判断玛丽与障碍物是否碰撞
                if pygame.sprite.collide_rect(marie, obstacle_list[i]):
                    # 发生碰撞，游戏结束
                    over = True
                    game_over()
                    music_button.bg_music.stop()
                else:
                    # 判断玛丽是否越过障碍物
                    if (obstacle_list[i].rect.x + obstacle_list[i].rect.width) < marie.rect.x:
                        # 加分
                        score += obstacle_list[i].get_score()
                # 显示分数
                obstacle_list[i].show_score(score)
            # 绘制播放音乐按钮
            SCREEN.blit(btn_img, (20, 20))

        # 增加障碍物时间
        addObstaleTimer += 20

        # 按时间更新窗口，先更新，再停顿
        pygame.display.update()
        FPSCLOCK.tick(FPS)


# 移动地图
class MyMap:

    def __init__(self, x, y):
        # 加载背景图片，载入图片之后进行转换为RGBA像素格式，Alpha为透明度
        self.bg = pygame.image.load("image/bg.png").convert_alpha()
        self.x = x
        self.y = y

    # 更新图片位置
    def map_rolling(self):
        if self.x < -790:
            # 移动结束，更新本张图片位置为默认的最后位置，等待下一次进入
            self.x = 800
        else:
            self.x -= 5

    # 更新地图
    def map_update(self):
        # Surface对象，将图片贴到自身上面，参数1：source，为一个Surface对象，参数2：元组，表示坐标
        SCREEN.blit(self.bg, (self.x, self.y))


# 跳动的玛丽类
class Marie:
    def __init__(self):
        # 初始化代表玛丽的矩形，左端点、上端点、宽度、高度
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.jumpState = False  # 跳跃的状态
        self.jumpHeight = 130  # 跳跃的高度
        self.lowest_y = 140  # 跳跃的最低坐标，画布中坐标y轴向下增大
        self.jumpValue = 0  # 跳跃增变量
        # 玛丽动图索引
        self.marieIndex = 0
        self.marieIndexGen = cycle([0, 1, 2])  # 以输入的列表为参数，生成无穷序列
        # 加载玛丽图片
        self.adventure_img = (
            pygame.image.load("image/adventure1.png").convert_alpha(),
            pygame.image.load("image/adventure2.png").convert_alpha(),
            pygame.image.load("image/adventure3.png").convert_alpha()
        )
        # 跳音效，mixer为用于加载和播放声音的模块
        self.jump_audio = pygame.mixer.Sound('audio/jump.wav')
        # 使用图片尺寸更新玛丽的矩形尺寸
        self.rect.size = self.adventure_img[0].get_size()
        # 玛丽默认显示的坐标位置
        self.x = 50
        self.y = self.lowest_y
        # 矩形左上角坐标
        self.rect.topleft = (self.x, self.y)

    # 跳跃的动作开关
    def jump(self):
        self.jumpState = True

    # 移动动作
    def move(self):
        if self.jumpState:
            if self.rect.y >= self.lowest_y:  # 起跳时已经站在地上了
                self.jumpValue = -5  # 以5个像素值向上移动
            if self.rect.y <= self.lowest_y - self.jumpHeight:  # 到达顶部回落
                self.jumpValue = 5
            self.rect.y += self.jumpValue  # 改变坐标
            if self.rect.y >= self.lowest_y:  # 回落到地上
                self.jumpState = False  # 关闭跳跃状态

    # 绘制
    def draw_marie(self):
        # 匹配动图
        marieIndex = next(self.marieIndexGen)
        # 绘制图像
        SCREEN.blit(self.adventure_img[marieIndex], (self.x, self.rect.y))


# 障碍物类
class Obstacle:
    score = 1  # 分数
    move = 5  # 单位时间移动距离，或称为移动速度
    obstacle_y = 150  # 障碍物坐标

    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        # 加载导弹图片、管道图片
        self.missile = pygame.image.load("image/missile.png").convert_alpha()
        self.pipe = pygame.image.load("image/pipe.png").convert_alpha()
        # 分数图片
        self.numbers = (
            pygame.image.load('image/0.png').convert_alpha(),
            pygame.image.load('image/1.png').convert_alpha(),
            pygame.image.load('image/2.png').convert_alpha(),
            pygame.image.load('image/3.png').convert_alpha(),
            pygame.image.load('image/4.png').convert_alpha(),
            pygame.image.load('image/5.png').convert_alpha(),
            pygame.image.load('image/6.png').convert_alpha(),
            pygame.image.load('image/7.png').convert_alpha(),
            pygame.image.load('image/8.png').convert_alpha(),
            pygame.image.load('image/9.png').convert_alpha()
        )
        # 加载加分音效
        self.score_audio = pygame.mixer.Sound('audio/score.wav')
        # 0 1随机数
        r = random.randint(0, 1)
        if r == 0:
            self.image = self.missile
            self.move = 15  # 导弹移动速度加快
            self.obstacle_y = 100
        else:
            self.image = self.pipe
        # 根据障碍物位图的高宽设置矩形
        self.rect.size = self.image.get_size()
        # 获取位图宽高
        self.width, self.height = self.rect.size
        # 障碍物绘制坐标
        self.x = 800
        self.y = self.obstacle_y
        self.rect.center = (self.x, self.y)

    # 障碍物移动
    def obstacle_move(self):
        self.rect.x -= self.move

    # 绘制障碍物
    def draw_obstacle(self):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))

    # 得分
    def get_score(self):
        temp = self.score
        if temp == 1:
            # 播放加分音乐
            self.score_audio.play()
        # 将障碍物的得分置0，否则会一直判断越过障碍物加分
        self.score = 0
        return temp

    # 显示指定分数
    def show_score(self, score):
        # 获取得分数字
        self.scoreDigits = [int(x) for x in list(str(score))]
        totalWidth = 0      # 要显示的所有数字的总宽度
        for digit in self.scoreDigits:
            # 获取积分图片的宽度
            totalWidth += self.numbers[digit].get_width()
        # 分数横向位置，右边空出30个像素点
        Xoffset = (SCREENWIDTH - (totalWidth + 30))
        for digit in self.scoreDigits:
            # 分数绘制
            SCREEN.blit(self.numbers[digit], (Xoffset, SCREENHEIGHT * 0.1))
            # 随数字增加改变位置
            Xoffset += self.numbers[digit].get_width()


# 背景音乐按钮
class Music_Button:
    is_open = True

    def __init__(self):
        # 背景音乐及其按钮（两个状态）
        self.bg_music = pygame.mixer.Sound('audio/bg_music.wav')
        self.open_img = pygame.image.load('image/btn_open.png').convert_alpha()
        self.close_img = pygame.image.load('image/btn_close.png').convert_alpha()

    # 判断鼠标是否在按钮范围内
    def is_select(self):
        # 获取鼠标位置
        point_x, point_y = pygame.mouse.get_pos()
        w, h = self.open_img.get_size()
        # 判断鼠标是否在按钮范围内，20为按钮x,y轴坐标
        in_x = 20 < point_x < 20 + w
        in_y = 20 < point_y < 20 + h
        return in_x and in_y

if __name__ == '__main__':
    mainGame()
