import argparse
import json
import logging
import os
import sys
import time

import cv2
import numpy as np
import PIL
import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data.distributed import DistributedSampler
from tqdm import tqdm

import _init_paths

from lib.utils.utils import *


def get_args():
    parser = argparse.ArgumentParser("ResNet20-Cifar100-oneshot-Test")

    parser.add_argument('--rank', default=0,
                        help='rank of current process')
    parser.add_argument(
        '--path', default="data/benchmark.json", help="path for json arch files")
    parser.add_argument('--batch-size', type=int,
                        default=1024, help='batch size')
    parser.add_argument('--workers', type=int,
                        default=3, help='num of workers')
    parser.add_argument('--weights', type=str,
                        default="./weights/2021Y_06M_01D_23H_0791/model-latest.th", help="path for weights loading")

    parser.add_argument('--local_rank', type=int, default=0,
                        help='local rank for distributed training')

    parser.add_argument('--min_lr', type=float,
                        default=5e-4, help='min learning rate')
    parser.add_argument('--momentum', type=float, default=0.9, help='momentum')
    parser.add_argument('--weight_decay', type=float,
                        default=4e-5, help='weight decay')
    parser.add_argument('--gpu', type=int, default=0, help='gpu device id')
    parser.add_argument('--seed', type=int, default=0, help='random seed')
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    num_gpus = torch.cuda.device_count()
    np.random.seed(args.seed)
    args.gpu = args.local_rank % num_gpus
    torch.cuda.set_device(args.gpu)

    cudnn.benchmark = True
    cudnn.deterministic = True
    torch.manual_seed(args.seed)
    cudnn.enabled = True
    torch.cuda.manual_seed(args.seed)

    if num_gpus > 1:
        torch.distributed.init_process_group(
            backend='nccl', init_method='env://')
        args.world_size = torch.distributed.get_world_size()
        args.batch_size = args.batch_size // args.world_size

    # Log
    log_format = '[%(asctime)s] %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format=log_format, datefmt='%d %I:%M:%S')
    t = time.time()
    local_time = time.localtime(t)
    if not os.path.exists('./log'):
        os.mkdir('./log')
    fh = logging.FileHandler(os.path.join(
        'log/train-{}{:02}{}'.format(local_time.tm_year % 2000, local_time.tm_mon, t)))
    fh.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(fh)

    # archLoader
    # arch_loader = ArchLoader(args.path)
    arch_dataset = ArchDataSet(args.path)
    arch_sampler = None
    if num_gpus > 1:
        arch_sampler = DistributedSampler(arch_dataset)

    arch_dataloader = torch.utils.data.DataLoader(
        arch_dataset, batch_size=1, shuffle=False, num_workers=3, pin_memory=True, sampler=arch_sampler)

    val_dataset = get_val_dataset()
    val_loader = torch.utils.data.DataLoader(val_dataset,
                                             batch_size=args.batch_size, shuffle=False,
                                             num_workers=args.workers, pin_memory=True)

    print('load data successfully')

    model = sample_resnet20()
    # model = dynamic_resnet20()

    print("load model successfully")

    print('load from latest checkpoint')
    lastest_model = args.weights
    if lastest_model is not None:
        checkpoint = torch.load(lastest_model)
        model.load_state_dict(checkpoint['state_dict'])

    model = model.cuda(args.gpu)
    # if num_gpus > 1:
    #     model = torch.nn.parallel.DistributedDataParallel(
    #         model, device_ids=[args.local_rank], output_device=args.local_rank, find_unused_parameters=False)

    # 参数设置
    args.val_dataloader = val_loader

    print("start to validate model...")

    validate(model, args, arch_loader=arch_dataloader)
    # angle_validate(model, arch_loader, args)


def validate(model, args, *, arch_loader=None):
    assert arch_loader is not None

    val_dataloader = args.val_dataloader

    t1 = time.time()

    result_dict = {}

    model.eval()

    arch_loader = tqdm(arch_loader)
    for key, arch in arch_loader:
        arch_list = [int(itm) for itm in arch[0].split('-')]

        with torch.no_grad():
            top1 = AvgrageMeter()
            for data, target in val_dataloader:  # 过一遍数据集

                data = data.cuda(args.gpu, non_blocking=True)
                target = target.cuda(args.gpu, non_blocking=True)

                output = model(data, arch_list)

                prec1, prec5 = accuracy(output, target, topk=(1, 5))

                n = data.size(0)
                top1.update(prec1.item(), n)

        tmp_dict = {}
        tmp_dict['arch'] = arch[0]
        tmp_dict['acc'] = top1.avg / 100

        result_dict[key[0]] = tmp_dict

        post_fix = {"top1": "%.4f" % (top1.avg/100)}
        arch_loader.set_postfix(log=post_fix)

    with open("acc_%s.json" % (args.path.split('/')[1].split('.')[0]), "w") as f:
        json.dump(result_dict, f)


if __name__ == "__main__":
    main()