



class warl_model:
    def __init__(self, checkpoint, config):
        self.checkpoint = checkpoint
        self.config = config
    
    def __call__(self, path_to_img):
        # print(path_to_img)
        num_warls = 5
        return path_to_img, num_warls