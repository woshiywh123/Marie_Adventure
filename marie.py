import pygame
from pygame.locals import *
from itertools import cycle
import sys

SCREENWIDTH = 822       # 窗口宽度
SCREENHEIGHT = 199      # 窗口高度
FPS = 30                # 窗口更新画面的时间

def mainGame():
    score = 0   # 得分
    over = False
    global SCREEN,  FPSCLOCK
    pygame.init()       # pygame初始化
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

    # 检查窗体的显示与刷新
    while True:
        # 获取单机事件，需要循环检查发生的每个事件
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()       # 退出窗口
                sys.exit()          # 关闭窗口
            # 判断是否按下了空格
            if event.type == KEYDOWN and event.key == K_SPACE:
                if marie.rect.y >= marie.lowest_y:      # 如果玛丽在地面上
                    marie.jump_audio.play()             # 播放跳跃音效
                    marie.jump()                        # 开启跳跃状态
        # 实现地图循环滚动
        if over == False:
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

        # 按时间更新窗口，先更新，再停顿
        pygame.display.update()
        FPSCLOCK.tick(FPS)
# 移动地图
class MyMap():

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
class Marie():
    def __init__(self):
        # 初始化代表玛丽的矩形，左端点、上端点、宽度、高度
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.jumpState = False      # 跳跃的状态
        self.jumpHeight = 130       # 跳跃的高度
        self.lowest_y = 140         # 跳跃的最低坐标，画布中坐标y轴向下增大
        self.jumpValue = 0          # 跳跃增变量
        # 玛丽动图索引
        self.marieIndex = 0
        self.marieIndexGen = cycle([0, 1, 2])       # 以输入的列表为参数，生成无穷序列
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
            if self.rect.y >= self.lowest_y:        # 起跳时已经在空中或者站在地上了
                self.jumpValue = -5                 # 以5个像素值向上移动
            if self.rect.y <= self.lowest_y - self.jumpHeight:      # 到达顶部回落
                self.jumpValue = 5
            self.rect.y += self.jumpValue       # 改变坐标
            if self.rect.y >= self.lowest_y:    # 回落到地上
                self.jumpState = False          # 关闭跳跃状态

    # 绘制
    def draw_marie(self):
        # 匹配动图
        marieIndex = next(self.marieIndexGen)
        # 绘制图像
        SCREEN.blit(self.adventure_img[marieIndex], (self.x, self.rect.y))



if __name__=='__main__':
    mainGame()