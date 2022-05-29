import os
from nn import WarlModel
import time

if __name__ == '__main__':
    checkpoint = "/home/hm/ml/hack-ai-walruses/app/checkpoints/cascade_mask_rcnn_x101_32x4d_fpn_1x_epoch_36.pth"
    config = "/home/hm/tmp/mmdetection/configs/cascade_rcnn/cascade_mask_rcnn_x101_32x4d_fpn_1x_coco.py"
    nn_model = WarlModel(checkpoint=checkpoint,
                         config=config)

    dir_img = './test_data'
    path_imgs = []
    for fname in os.listdir(dir_img):
        fpath = os.path.join(dir_img, fname)
        if not os.path.isfile(fpath):
            continue
        f_ext = fname.split(".")[-1]
        if f_ext.lower() in ['jpg', 'jpeg', 'png', 'bmp']:
            path_imgs.append(fpath)

    for id_img, path_img in enumerate(path_imgs):
        print(f"{id_img}/{len(path_imgs)}, {path_img}")
        start_time = time.time()
        path_img_predict, num_warls = nn_model(path_img=path_img, score_thr=0.001)
        end_time = time.time()
        print(f"{path_img_predict}, count_warls: {num_warls}, time_inference: {end_time-start_time}")
