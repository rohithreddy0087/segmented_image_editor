import numpy as np

def color_map(N=256, normalized=False):
    def bitget(byteval, idx):
        return ((byteval & (1 << idx)) != 0)

    dtype = 'float32' if normalized else 'uint8'
    cmap = np.zeros((N, 3), dtype=dtype)
    for i in range(N):
        r = g = b = 0
        c = i
        for j in range(8):
            r = r | (bitget(c, 0) << 7-j)
            g = g | (bitget(c, 1) << 7-j)
            b = b | (bitget(c, 2) << 7-j)
            c = c >> 3

        cmap[i] = np.array([r, g, b])

    cmap = cmap/255 if normalized else cmap
    return cmap

def get_max_coordinates(image_array):
    max_value = np.max(image_array)
    max_indices = np.where(image_array == max_value)
    row_coordinates = max_indices[0]
    column_coordinates = max_indices[1]
    return [row_coordinates[0], column_coordinates[0]]

class BatchColorize(object):
    def __init__(self, n=150):
        self.cmap = color_map(n)
        # print(self.cmap[170:172])
        # self.cmap = torch.from_numpy(self.cmap[:n])

    def __call__(self, gray_image):
        size = gray_image.shape
        color_image = np.zeros((size[0], 3, size[1], size[2]), dtype=np.uint8)

        for label in range(0, len(self.cmap)):
            mask = (label == gray_image)
            color_image[:,0][mask] = self.cmap[label][0]
            color_image[:,1][mask] = self.cmap[label][1]
            color_image[:,2][mask] = self.cmap[label][2]

        # handle void
        mask = (255 == gray_image)
        color_image[:,0][mask] = color_image[:,1][mask] = color_image[:,2][mask] = 255

        return color_image
    
class BatchDeColorize(object):
    def __init__(self, n=40):
        self.cmap = color_map(n)

    def __call__(self, rgb_image, return_points=False, dst=''):
        size = rgb_image.shape
        gray_image = np.zeros((size[0], size[1], size[2]), dtype=np.float32) - 1
        eps1 = 28
        eps = eps1
        pts = []
        for label in range(0, len(self.cmap)):
            tmp = np.zeros_like(rgb_image, dtype=int)
            tmp[...,0] = self.cmap[label][0]
            tmp[...,1] = self.cmap[label][1]
            tmp[...,2] = self.cmap[label][2]
            # mask = (tmp == rgb_image)
            # m = np.prod(mask, -1).astype(bool)   
                
            m11 = np.maximum(tmp[...,0] - eps1, 0) <= rgb_image[...,0]
            m12 = rgb_image[...,0] <= np.minimum(tmp[...,0] + eps, 255)
            m21 = np.maximum(tmp[...,1] - eps1, 0) <= rgb_image[...,1] 
            m22 = rgb_image[...,1] <= np.minimum(tmp[...,1] + eps, 255)
            m31 = np.maximum(tmp[...,2] - eps1, 0) <= rgb_image[...,2]
            m32 = rgb_image[...,2] <= np.minimum(tmp[...,2] + eps, 255)
            m1 = np.logical_and(m11, m12)
            m2 = np.logical_and(m21, m22)
            m3 = np.logical_and(m31, m32) 
            m = np.logical_and(m1, m2)
            m = np.logical_and(m, m3) 
          
            gray_image[m] = label            
            if return_points:
                m11 = np.maximum(tmp[...,0] - eps1, 0) <= rgb_image[...,0]
                m12 = rgb_image[...,0] <= np.minimum(tmp[...,0] + eps, 255)
                m21 = np.maximum(tmp[...,1] - eps1, 0) <= rgb_image[...,1] 
                m22 = rgb_image[...,1] <= np.minimum(tmp[...,1] + eps, 255)
                m31 = np.maximum(tmp[...,2] - eps1, 0) <= rgb_image[...,2]
                m32 = rgb_image[...,2] <= np.minimum(tmp[...,2] + eps, 255)
                m1 = np.logical_and(m11, m12)
                m2 = np.logical_and(m21, m22)
                m3 = np.logical_and(m31, m32) 
                m = np.logical_and(m1, m2)
                m = np.logical_and(m, m3) 
                pts.append(get_max_coordinates(m*1))

        # handle void
        mask = (-1 == gray_image)
        gray_image[mask] = 255
        if return_points:
            return pts
        return gray_image[0]
    
class_color = color_map()
class_dict = {
                183: "unlabeled",
                1: "person",
                2: "bicycle",
                3: "car",
                4: "motorcycle",
                5: "airplane",
                6: "bus",
                7: "train",
                8: "truck",
                9: "boat",
                10: "traffic light",
                11: "fire hydrant",
                12: "street sign",
                13: "stop sign",
                14: "parking meter",
                15: "bench",
                16: "bird",
                17: "cat",
                18: "dog",
                19: "horse",
                20: "sheep",
                21: "cow",
                22: "elephant",
                23: "bear",
                24: "zebra",
                25: "giraffe",
                26: "hat",
                27: "backpack",
                28: "umbrella",
                29: "shoe",
                30: "eye glasses",
                31: "handbag",
                32: "tie",
                33: "suitcase",
                34: "frisbee",
                35: "skis",
                36: "snowboard",
                37: "sports ball",
                38: "kite",
                39: "baseball bat",
                40: "baseball glove",
                41: "skateboard",
                42: "surfboard",
                43: "tennis racket",
                44: "bottle",
                45: "plate",
                46: "wine glass",
                47: "cup",
                48: "fork",
                49: "knife",
                50: "spoon",
                51: "bowl",
                52: "banana",
                53: "apple",
                54: "sandwich",
                55: "orange",
                56: "broccoli",
                57: "carrot",
                58: "hot dog",
                59: "pizza",
                60: "donut",
                61: "cake",
                62: "chair",
                63: "couch",
                64: "potted plant",
                65: "bed",
                66: "mirror",
                67: "dining table",
                68: "window",
                69: "desk",
                70: "toilet",
                71: "door",
                72: "tv",
                73: "laptop",
                74: "mouse",
                75: "remote",
                76: "keyboard",
                77: "cell phone",
                78: "microwave",
                79: "oven",
                80: "toaster",
                81: "sink",
                82: "refrigerator",
                83: "blender",
                84: "book",
                85: "clock",
                86: "vase",
                87: "scissors",
                88: "teddy bear",
                89: "hair drier",
                90: "toothbrush",
                91: "hair brush",
                92: "banner",
                93: "blanket",
                94: "branch",
                95: "bridge",
                96: "building-other",
                97: "bush",
                98: "cabinet",
                99: "cage",
                100: "cardboard",
                101: "carpet",
                102: "ceiling-other",
                103: "ceiling-tile",
                104: "cloth",
                105: "clothes",
                106: "clouds",
                107: "counter",
                108: "cupboard",
                109: "curtain",
                110: "desk-stuff",
                111: "dirt",
                112: "door-stuff",
                113: "fence",
                114: "floor-marble",
                115: "floor-other",
                116: "floor-stone",
                117: "floor-tile",
                118: "floor-wood",
                119: "flower",
                120: "fog",
                121: "food-other",
                122: "fruit",
                123: "furniture-other",
                124: "grass",
                125: "gravel",
                126: "ground-other",
                127: "hill",
                128: "house",
                129: "leaves",
                130: "light",
                131: "mat",
                132: "metal",
                133: "mirror-stuff",
                134: "moss",
                135: "mountain",
                136: "mud",
                137: "napkin",
                138: "net",
                139: "paper",
                140: "pavement",
                141: "pillow",
                142: "plant-other",
                143: "plastic",
                144: "platform",
                145: "playingfield",
                146: "railing",
                147: "railroad",
                148: "river",
                149: "road",
                150: "rock",
                151: "roof",
                152: "rug",
                153: "salad",
                154: "sand",
                155: "sea",
                156: "shelf",
                157: "sky-other",
                158: "skyscraper",
                159: "snow",
                160: "solid-other",
                161: "stairs",
                162: "stone",
                163: "straw",
                164: "structural-other",
                165: "table",
                166: "tent",
                167: "textile-other",
                168: "towel",
                169: "tree",
                170: "vegetable",
                171: "wall-brick",
                172: "wall-concrete",
                173: "wall-other",
                174: "wall-panel",
                175: "wall-stone",
                176: "wall-tile",
                177: "wall-wood",
                178: "water-other",
                179: "waterdrops",
                180: "window-blind",
                181: "window-other",
                182: "wood"
            }
