#!/user/bin/python3
# @File    : ImageTest.py
# @Software: PyCharm



# 导入所需Package
# import cv2
from cv2 import resize, cvtColor, Laplacian, CV_64F, COLOR_BGR2GRAY, INTER_CUBIC
import numpy as np



def image_processing(threshold_min, threshold_max, image, ui):
    imagenum = np.asarray(image)
    imsize = imagenum.shape
    imagenum = resize(imagenum, (int(imsize[1] / 2), int(imsize[0] / 2)), interpolation=INTER_CUBIC)
    gray = cvtColor(imagenum, COLOR_BGR2GRAY)
    imageVar = Laplacian(gray, CV_64F).var()
    if imageVar < threshold_min or imageVar > threshold_max:
        result = 1
    else:
        result = 0
    return result, imageVar


# # 方法二：保存图片并判断
#
# t = 10
# dirpath = './image0/'
# thresholdmin = 300
# thresholdmax = 2500
#
# for x in range(t):
#     image = ImageGrab.grab()
#     image.save(dirpath + str(x) + ".png")
#
# if os.path.isdir(dirpath) == False:
#     raise AssertionError
#
# files = os.listdir(dirpath)
#
# for filename in files:
#
#     file = os.path.join(dirpath, filename)
#
#     image = cv2.imread(file)
#
#     imsize = image.shape
#
#     image = cv2.resize(image, (int(imsize[1]/2), int(imsize[0]/2)), interpolation=cv2.INTER_CUBIC)
#
#     # cv2.imshow('', image)
#     # cv2.waitKey(0)
#
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     # cv2.imshow('', gray)
#     # cv2.waitKey(0)
#
#     imageVar = cv2.Laplacian(gray, cv2.CV_64F).var()
#
#     if imageVar < thresholdmin or imageVar > thresholdmax:
#         # cv2.imshow('', image)
#         # cv2.waitKey(0)
#         print(filename + '  imageVar: %d' % (imageVar))
#         cv2.imwrite("./imagefail/" + str(x) + ".png",image)


# if __name__ == '__main__':
#     file = readDataset('./image')
#     plt.imshow(data[0])
#     plt.show()

# cv2.imshow('', gray)
# cv2.waitKey(2000)
# plt.imshow(image/255)
# plt.show()

# def readDataset(dirpath, shape, mode=0):
#     if os.path.isdir(dirpath) == False:
#         raise AssertionError
#     files = os.listdir(dirpath)
#     files_num = len(files)
#     if mode == 0:
#         data = np.zeros(shape=(files_num,shape[0],shape[1],shape[2]))
#     else:
#         data = ['']*files_num
#
#     i = 0
#     for filename in files:
#         filename = os.path.join(dirpath,filename)
#         # print(filename)
#         if mode == 0:
#             image = cv2.imread(filename)
#             image = cv2.resize(image, shape[:2], interpolation=cv2.INTER_CUBIC)
#             data[i] = image / 255
#         else:
#             data[i] = filename
#         i += 1
#     return data
#
# if __name__ == '__main__':
#     data = readDataset('./image',)
#     plt.imshow(data[0])
#     plt.show()

