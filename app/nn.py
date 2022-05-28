import os.path

import cv2
import mmcv
from mmcv import Config
from mmcv.runner import load_checkpoint
import matplotlib.pyplot as plt

from mmdet.datasets import build_dataset
from mmdet.models import build_detector
from mmdet.apis import train_detector
from mmdet.apis import inference_detector, show_result_pyplot
import os.path as osp
from .utils import *


class warl_model:
    def __init__(self, checkpoint, config, device: str="cpu"):
        self.checkpoint_path = checkpoint
        self.config_path = config
        self.device = device

        self.model = None
        self.checkpoint = None
        self.cfg_model = None

    def load_config(self):
        self.cfg_model.dataset_type = 'COCODataset'
        self.cfg_model = Config.fromfile(self.config_path)
        self.cfg_model.device = self.device
        self.cfg_model.data.workers_per_gpu = 0
        if "cascade_rcnn" in self.config_path:
            self.cfg_model.model.roi_head.bbox_head[0].num_classes = 1
            self.cfg_model.model.roi_head.bbox_head[1].num_classes = 1
            self.cfg_model.model.roi_head.bbox_head[2].num_classes = 1
            self.cfg_model.model.roi_head.mask_head.num_classes = 1
        elif "mask_rcnn" in self.config_path:
            self.cfg_model.model.roi_head.bbox_head.num_classes = 1
            self.cfg_model.model.roi_head.mask_head.num_classes = 1
        else:
            return False
        return True

    def load_model(self):
        if self.cfg_model is None:
            return False
        self.model = build_detector(self.cfg_model.model)
        self.model.CLASSES = ('walrus',)
        self.checkpoint = load_checkpoint(self.model, self.checkpoint_path, map_location=self.device)
        self.model.CLASSES = self.checkpoint['meta']['CLASSES']
        # We need to set the model's cfg for inference
        self.model.cfg = self.cfg_model

        # Convert the model to GPU
        self.model.to(self.device)
        # Convert the model into evaluation mode
        self.model.eval()
        return True

    def inference(self, img):
        result = inference_detector(self.model, img)
        bboxes = result[0]
        masks = result[1]
        return bboxes, masks

    def __call__(self, path_img: str, score_thr: float = 0.01):
        """
        model trained size by (1333, 800)
        :param path_img:
        :param score_thr:
        :return:
        """

        # print(path_to_img)
        if (self.model is None) or (self.cfg_model is None):
            return None

        img_orig = mmcv.imread(path_img)
        img = img_orig.copy()
        height, width = img.shape[:2]
        scale_coef = 1
        if height > 800:
            scale_coef = 800/height
        if scale_coef != 1:
            new_height, new_width = height * scale_coef, width * scale_coef
            img = cv2.resize(img_orig, (new_height, new_width))

        # инференс скользящим окном?

        bboxes, masks = self.inference(img)
        if scale_coef != 1:
            boxes, masks = restore_predict(img_orig, img, bboxes, masks)

        bboxes, masks, polygons = self.postprocessing(bboxes, masks, score_thr)
        # img_predict = show_result_pyplot(self.model, img, result, score_thr=0.01)

        path_img_dir = os.path.dirname(path_img)
        img_basename = os.path.basename(path_img)
        ext_img = img_basename.split(".")[-1]
        path_img_predict = os.path.join(path_img_dir, img_basename.replace(f".{ext_img}", f"_predict.jpg"))

        img_predict = plot_result(img_orig, bboxes, masks, polygons)
        cv2.imwrite(path_img_predict, img_predict)

        num_warls = 5
        return path_img_predict, num_warls

    def postprocessing(self, bboxes, masks, score_thr: float = 0.01):
        filter_bboxes = []
        filter_masks = []
        for bbox, mask in zip(bboxes, masks):
            xtl, ytl, xbr, tbr, conf = bbox
            if conf >= score_thr:
                filter_bboxes.append(bbox)
                filter_masks.append(masks)

        # masks to contours
        filter_contours = []
        for bw_mask in filter_masks:
            #bw_mask must black white
            contours, hierarchy = cv2.findContours(bw_mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            max_area_contour = max(contours, key= lambda cnt: cv2.contourArea(cnt))
            poly = max_area_contour.transpose(1, 0, 2)[0]
            filter_contours.append(poly)

        return filter_bboxes, filter_masks, filter_contours

    def get_centre_objects(self, polygons):
        poly_centres = []
        for poly in polygons:
            count_points = poly.shape[0]
            if count_points <= 2:
                continue
            geom_poly = Polygon(poly)
            poly_centre = geom_poly.centroid
            poly_centres.append([poly_centre.x, poly_centre.y])

        # если точки слишком близко - то они объединяются
        return  poly_centres









