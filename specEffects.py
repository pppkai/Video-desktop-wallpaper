# -*- coding: utf-8 -*-

from PIL import Image, ImageFilter
from myLog import log
import numpy as np
import cv2, math, random


class SpecEffects(object):
    def __init__(self, im_path=None):
        super(SpecEffects, self).__init__()
        self.im_path = im_path
        self.logger = log('in SpecEffects')


    def __set__(self, obj, val):
        self.obj = val


    """ PIL特效十选一 """
    def effectByPILFilter(self, index=None, im_file=None):
        self.logger.info('effectByPILFilter index:%s im_file:%s' % (index, im_file))

        im = Image.open(self.im_path if im_file is None else im_file)
        random_index = random.randint(0, 9) if index is None else index

        # [模糊, 200模糊, 轮廓滤波, 锐化, 浮雕滤波, 寻找边缘信息的滤波]
        filters = [ImageFilter.BLUR, ImageFilter.BoxBlur(200), ImageFilter.CONTOUR, ImageFilter.EDGE_ENHANCE, ImageFilter.EMBOSS, ImageFilter.FIND_EDGES]

        # 彩色转黑白
        def blackWithe(imagename):
            # r,g,b = r*0.299+g*0.587+b*0.114
            im = np.asarray(Image.open(imagename).convert('RGB'))
            trans = np.array([[0.299, 0.587, 0.114], [0.299, 0.587, 0.114], [0.299, 0.587, 0.114]]).transpose()
            im = np.dot(im, trans)
            return Image.fromarray(np.array(im).astype('uint8'))

        # 流年
        def fleeting(imagename, params=12):
            im = np.asarray(Image.open(imagename).convert('RGB'))
            im1 = np.sqrt(im * [1.0, 0.0, 0.0]) * params
            im2 = im * [0.0, 1.0, 1.0]
            im = im1 + im2
            return Image.fromarray(np.array(im).astype('uint8'))

        # 旧电影
        def oldFilm(imagename):
            im = np.asarray(Image.open(imagename).convert('RGB'))
            # r=r*0.393+g*0.769+b*0.189 g=r*0.349+g*0.686+b*0.168 b=r*0.272+g*0.534b*0.131
            trans = np.array([[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]).transpose()
            # clip 超过255的颜色置为255
            im = np.dot(im, trans).clip(max=255)
            return Image.fromarray(np.array(im).astype('uint8'))

        # 反色
        def reverse(imagename):
            im = 255 - np.asarray(Image.open(imagename).convert('RGB'))
            return Image.fromarray(np.array(im).astype('uint8'))

        if random_index > 5:
            to_choice = {
                'func1': blackWithe,
                'func2': fleeting,
                'func3': oldFilm,
                'func4': reverse,
            }
            im_filter = to_choice.get('func' + str(random_index-5), fleeting)(self.im_path if im_file is None else im_file)
        else:
            im_filter = im.filter(filters[random_index])

        return cv2.cvtColor(np.asarray(im_filter), cv2.COLOR_RGB2BGR)


    """ CV2特效十选一 """
    def effectByCV2(self, index=None, im_file=None):
        self.logger.info('effectByCV2 index:%s im_file:%s' % (index, im_file))

        # 毛玻璃特效
        def maoboli(imagename):
            src = cv2.imread(imagename)
            dst = np.zeros_like(src)
            rows, cols = src.shape[:2]
            offsets = 5
            random_num = 0
            for y in range(rows - offsets):
                for x in range(cols - offsets):
                    random_num = np.random.randint(0, offsets)
                    dst[y, x] = src[y + random_num, x + random_num]
            return dst

        # 浮雕效果
        def fudiao(imagename):
            img = cv2.imread(imagename, 1)
            height, width = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            dstImg = np.zeros((height, width, 1), np.uint8)

            # 浮雕特效算法：newPixel = grayCurrentPixel - grayNextPixel + 150
            for i in range(0, height):
                for j in range(0, width - 1):
                    grayCurrentPixel = int(gray[i, j])
                    grayNextPixel = int(gray[i, j + 1])
                    newPixel = grayCurrentPixel - grayNextPixel + 150
                    if newPixel > 255:
                        newPixel = 255
                    if newPixel < 0:
                        newPixel = 0
                    dstImg[i, j] = newPixel

            return dstImg

        # 油漆效果
        def yuqi(imagename):
            src = cv2.imread(imagename)
            gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

            # 自定义卷积核
            kernel = np.array([[-1, -1, -1], [-1, 10, -1], [-1, -1, -1]])
            # kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
            return cv2.filter2D(gray, -1, kernel)

        # 素描特效
        def shumiao(imagename):
            img = cv2.imread(imagename)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 高斯滤波降噪
            gaussian = cv2.GaussianBlur(gray, (5, 5), 0)

            # Canny算子
            canny = cv2.Canny(gaussian, 50, 150)

            # 阈值化处理
            ret, result = cv2.threshold(canny, 100, 255, cv2.THRESH_BINARY_INV)
            return result

        # 素描特效2
        def shumiao2(imagename, mask=60):
            image = cv2.imread(imagename)
            width, height = image.shape[:2]
            blend = np.zeros((width, height), np.uint8)
            for col in range(width):
                for row in range(height):
                    # do for every pixel
                    if mask[col, row] == 255:
                        # avoid division by zero
                        blend[col, row] = 255
                    else:
                        # shift image pixel value by 8 bits
                        # divide by the inverse of the mask
                        tmp = (image[col, row] << 8) / (255 - mask)
                        # print('tmp={}'.format(tmp.shape))
                        # make sure resulting value stays within bounds
                        if tmp.any() > 255:
                            tmp = 255
                            blend[col, row] = tmp
            return blend

        # 怀旧特效
        def huaijiu(imagename):
            img = cv2.imread(imagename)
            rows, cols = img.shape[:2]
            dst = np.zeros((rows, cols, 3), dtype="uint8")
            for i in range(rows):
                for j in range(cols):
                    B = 0.272 * img[i, j][2] + 0.534 * img[i, j][1] + 0.131 * img[i, j][0]
                    G = 0.349 * img[i, j][2] + 0.686 * img[i, j][1] + 0.168 * img[i, j][0]
                    R = 0.393 * img[i, j][2] + 0.769 * img[i, j][1] + 0.189 * img[i, j][0]
                    if B > 255:
                        B = 255
                    if G > 255:
                        G = 255
                    if R > 255:
                        R = 255
                    dst[i, j] = np.uint8((B, G, R))

            return dst

        # 光照特效
        def guangz(imagename):
            img = cv2.imread(imagename)
            rows, cols = img.shape[:2]

            # 设置中心点
            centerX = rows / 2
            centerY = cols / 2
            radius = min(centerX, centerY)

            # 设置光照强度
            strength = 200

            dst = np.zeros((rows, cols, 3), dtype="uint8")
            for i in range(rows):
                for j in range(cols):
                    # 计算当前点到光照中心的距离(平面坐标系中两点之间的距离)
                    distance = math.pow((centerY - j), 2) + math.pow((centerX - i), 2)
                    # 获取原始图像
                    B = img[i, j][0]
                    G = img[i, j][1]
                    R = img[i, j][2]
                    if (distance < radius * radius):
                        # 按照距离大小计算增强的光照值
                        result = (int)(strength * (1.0 - math.sqrt(distance) / radius))
                        B = img[i, j][0] + result
                        G = img[i, j][1] + result
                        R = img[i, j][2] + result
                        # 判断边界 防止越界
                        B = min(255, max(0, B))
                        G = min(255, max(0, G))
                        R = min(255, max(0, R))
                        dst[i, j] = np.uint8((B, G, R))
                    else:
                        dst[i, j] = np.uint8((B, G, R))
            return dst

        # 流年特效
        def liunian(imagename):
            img = cv2.imread(imagename)

            # 获取图像行和列
            rows, cols = img.shape[:2]

            # 新建目标图像
            dst = np.zeros((rows, cols, 3), dtype="uint8")

            # 图像流年特效
            for i in range(rows):
                for j in range(cols):
                    # B通道的数值开平方乘以参数12
                    B = math.sqrt(img[i, j][0]) * 12
                    G = img[i, j][1]
                    R = img[i, j][2]
                    if B > 255:
                        B = 255
                    dst[i, j] = np.uint8((B, G, R))

            return dst

        # 水波特效
        def shuibo(imagename):
            img = cv2.imread(imagename)
            rows, cols = img.shape[:2]

            # 新建目标图像
            dst = np.zeros((rows, cols, 3), dtype="uint8")

            # 定义水波特效参数
            wavelength = 20
            amplitude = 30
            phase = math.pi / 4

            # 获取中心点
            centreX = 0.5
            centreY = 0.5
            radius = min(rows, cols) / 2

            # 设置水波覆盖面积
            icentreX = cols * centreX
            icentreY = rows * centreY

            # 图像水波特效
            for i in range(rows):
                for j in range(cols):
                    dx = j - icentreX
                    dy = i - icentreY
                    distance = dx * dx + dy * dy

                    if distance > radius * radius:
                        x = j
                        y = i
                    else:
                        # 计算水波区域
                        distance = math.sqrt(distance)
                        amount = amplitude * math.sin(distance / wavelength * 2 * math.pi - phase)
                        amount = amount * (radius - distance) / radius
                        amount = amount * wavelength / (distance + 0.0001)
                        x = j + dx * amount
                        y = i + dy * amount

                    # 边界判断
                    if x < 0:
                        x = 0
                    if x >= cols - 1:
                        x = cols - 2
                    if y < 0:
                        y = 0
                    if y >= rows - 1:
                        y = rows - 2

                    p = x - int(x)
                    q = y - int(y)

                    # 图像水波赋值
                    dst[i, j, :] = (1 - p) * (1 - q) * img[int(y), int(x), :] + p * (1 - q) * img[int(y), int(x), :] \
                    + (1 - p) * q * img[int(y), int(x), :] + p * q * img[int(y), int(x), :]

            return dst

        # 卡通特效
        def katong(imagename):
            img = cv2.imread(imagename)
            num_bilateral = 7
            img_color = img

            # 双边滤波处理
            for i in range(num_bilateral):
                img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)

            # 灰度图像转换
            img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            # 中值滤波处理
            img_blur = cv2.medianBlur(img_gray, 7)

            # 边缘检测及自适应阈值化处理
            img_edge = cv2.adaptiveThreshold(
                img_blur, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                blockSize=9,
                C=2
            )

            # 转换回彩色图像
            img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)

            # 与运算
            img_cartoon = cv2.bitwise_and(img_color, img_edge)

            return img_cartoon

        # 滤镜特效
        def lvjing(imagename):
            # 获取滤镜颜色
            def getBGR(img, table, i, j):
                # 获取图像颜色
                b, g, r = img[i][j]
                # 计算标准颜色表中颜色的位置坐标
                x = int(g / 4 + int(b / 32) * 64)
                y = int(r / 4 + int((b % 32) / 4) * 64)
                # 返回滤镜颜色表中对应的颜色
                return lj_map[x][y]

            img = cv2.imread(imagename)
            lj_map = cv2.imread('./res/lvj_map.png')

            rows, cols = img.shape[:2]
            dst = np.zeros((rows, cols, 3), dtype="uint8")

            # 循环设置滤镜颜色
            for i in range(rows):
                for j in range(cols):
                    dst[i][j] = getBGR(img, lj_map, i, j)

            return dst

        # 直方图
        def zifangtu(imagename):
            img = cv2.imread(imagename)

            # 提取三个颜色通道
            (b, g, r) = cv2.split(img)

            # 彩色图像均衡化
            bH = cv2.equalizeHist(b)
            gH = cv2.equalizeHist(g)
            rH = cv2.equalizeHist(r)

            # 合并通道
            return cv2.merge((bH, gH, rH))

        # 模糊特效
        def mohu(imagename):
            return cv2.GaussianBlur(cv2.cvtColor(cv2.imread(imagename), cv2.COLOR_BGR2RGB), (11, 11), 0)

        to_choice = {
            'func1': maoboli,
            'func2': fudiao,
            'func3': yuqi,
            'func4': shumiao,
            'func5': shumiao2,
            'func6': huaijiu,
            'func7': guangz,
            'func8': liunian,
            'func9': shuibo,
            'func10': katong,
            'func11': lvjing,
            'func12': zifangtu,
            'func13': mohu,
        }
        random_index = random.randint(0, 12) if index is None else index
        return to_choice.get('func' + str(random_index), lvjing)(self.im_path if im_file is None else im_file)