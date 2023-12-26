import os
import argparse
from fastsam import FastSAM, FastSAMPrompt
import ast
import torch
import numpy as np
import pandas as pd
from PIL import Image
from utils.tools import convert_box_xywh_to_xyxy

# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--model_path", type=str, default="./weights/FastSAM-x.pt", help="model"
#     )
#     parser.add_argument(
#         "--img_path", type=str, default="./uploads/", help="path to image folder"
#     )
#     parser.add_argument("--imgsz", type=int, default=1024, help="image size")
#     parser.add_argument(
#         "--iou",
#         type=float,
#         default=0.9,
#         help="iou threshold for filtering the annotations",
#     )
#     parser.add_argument(
#         "--text_prompt", type=str, default="leaf", help='use text prompt eg: "a dog"'
#     )
#     parser.add_argument(
#         "--conf", type=float, default=0.4, help="object confidence threshold"
#     )
#     parser.add_argument(
#         "--output", type=str, default="./output/", help="image save path"
#     )
#     parser.add_argument(
#         "--randomcolor", type=bool, default=True, help="mask random color"
#     )
#     parser.add_argument(
#         "--point_prompt", type=str, default="[[0,0]]", help="[[x1,y1],[x2,y2]]"
#     )
#     parser.add_argument(
#         "--point_label",
#         type=str,
#         default="[0]",
#         help="[1,0] 0:background, 1:foreground",
#     )
#     parser.add_argument("--box_prompt", type=str, default="[[0,0,0,0]]",
#                         help="[[x,y,w,h],[x2,y2,w2,h2]] support multiple boxes")
#     parser.add_argument(
#         "--better_quality",
#         type=str,
#         default=False,
#         help="better quality using morphologyEx",
#     )
#     device = torch.device(
#         "cuda"
#         if torch.cuda.is_available()
#         else "mps"
#         if torch.backends.mps.is_available()
#         else "cpu"
#     )
#     parser.add_argument(
#         "--device", type=str, default=device, help="cuda:[0,1,2,3,4] or cpu"
#     )
#     parser.add_argument(
#         "--retina",
#         type=bool,
#         default=True,
#         help="draw high-resolution segmentation masks",
#     )
#     parser.add_argument(
#         "--withContours", type=bool, default=False, help="draw the edges of the masks"
#     )
#     args = parser.parse_args()
#     return args

def get_config():
    args = argparse.Namespace()
    args.model_path = "./weights/FastSAM-x.pt"
    args.img_path = "./uploads/"
    args.imgsz = 1024
    args.iou = 0.9
    args.text_prompt = "leaf"
    args.conf = 0.4
    args.output = "./output/"
    args.randomcolor = True
    args.point_prompt = "[[0,0]]"
    args.point_label = "[0]"
    args.box_prompt = "[[0,0,0,0]]"
    args.better_quality = False
    args.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    args.retina = True
    args.withContours = False
    return args

def process_image(img_path, args):
    model = FastSAM(args.model_path)
    args.point_prompt = ast.literal_eval(args.point_prompt)
    args.box_prompt = convert_box_xywh_to_xyxy(ast.literal_eval(args.box_prompt))
    args.point_label = ast.literal_eval(args.point_label)
    input = Image.open(img_path)
    input = input.convert("RGB")
    everything_results = model(
        input,
        device=args.device,
        retina_masks=args.retina,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou
    )
    bboxes = None
    points = None
    point_label = None
    prompt_process = FastSAMPrompt(input, everything_results, device=args.device)
    if args.box_prompt[0][2] != 0 and args.box_prompt[0][3] != 0:
        ann = prompt_process.box_prompt(bboxes=args.box_prompt)
        bboxes = args.box_prompt

    elif args.text_prompt != None:
        ann = prompt_process.text_prompt(text=args.text_prompt)
        pixel_count = np.sum(ann)
        leaf_area = pixel_count * 0.000508
        leaf_area = round(leaf_area, 2)
        print("실제 잎의 면적: ", leaf_area, 'cm^2')

    elif args.point_prompt[0] != [0, 0]:
        ann = prompt_process.point_prompt(
            points=args.point_prompt, pointlabel=args.point_label
        )
        points = args.point_prompt
        point_label = args.point_label
    else:
        ann = prompt_process.everything_prompt()

    output_filename = os.path.splitext(os.path.basename(img_path))[0] + '.jpg'
    output_path = os.path.join(args.output, output_filename)

    prompt_process.plot(
        annotations=ann,
        output_path=output_path,
        bboxes=bboxes,
        points=points,
        point_label=point_label,
        withContours=args.withContours,
        better_quality=args.better_quality,
    )

    return leaf_area

def main(args):
    original_point_prompt = args.point_prompt
    original_box_prompt = args.box_prompt
    original_point_label = args.point_label

    results = []
    image_names = []
    for img_file in sorted(os.listdir(args.img_path)):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(args.img_path, img_file)
            args.point_prompt = original_point_prompt
            args.box_prompt = original_box_prompt
            args.point_label = original_point_label
            results.append(process_image(img_path, args))
            image_names.append(img_file)

    df = pd.DataFrame({'Filename': image_names, 'Leaf_Area': results})
    df.to_csv('results.csv', index=False)

    print(results)

if __name__ == "__main__":
    args = get_config()
    main(args)
