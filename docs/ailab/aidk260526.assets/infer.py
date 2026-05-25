import argparse
import functools
import os
import time

import cv2
from utils.predictor import Predictor
from utils.utils import add_arguments, print_arguments

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
add_arg('image_path',               str,     'dataset/test.jpg',                 '预测图片路径')
add_arg('face_db_path',             str,     'face_db',                          '人脸库路径')
add_arg('threshold',                float,   0.6,                                '判断相识度的阈值')
add_arg('mobilefacenet_model_path', str,     'save_model/mobilefacenet.pth',     'MobileFaceNet预测模型的路径')
add_arg('mtcnn_model_path',         str,     'save_model/mtcnn',                 'MTCNN预测模型的路径')
args = parser.parse_args()
print_arguments(args)


def main():
    predictor = Predictor(args.mtcnn_model_path, args.mobilefacenet_model_path, args.face_db_path, threshold=args.threshold)
    start = time.time()
    results = predictor.recognition(args.image_path)
    print('识别结果：', results)
    print(f'总识别时间：{int((time.time() - start) * 1000)}ms')
    
    # 始终保存结果图片
    image = predictor.draw_face(args.image_path, results)
    cv2.imwrite('result.jpg', image)
    print("结果已保存为 result.jpg")
    
    # 如果有显示环境，则显示图像窗口（按任意键关闭）
    if os.environ.get('DISPLAY'):
        cv2.imshow("result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("未检测到显示器，跳过图像窗口显示")


if __name__ == '__main__':
    main()
