# A PyTorch implementation of RICAP
This repository contains code for a data augmentation method **RICAP (Random Image Cropping And Patching)** based on [Data Augmentation using Random Image Cropping and Patching for Deep CNNs](https://arxiv.org/abs/1811.09030) implemented in PyTorch.

![example](example.png)

## Requirements
- Python 3.6
- PyTorch 0.4 or 1.0

## Training
### CIFAR-10
WideResNet28-10 baseline on CIFAR-10:
```
python train.py --dataset cifar10
```
WideResNet28-10 +RICAP on CIFAR-10:
```
python train.py --dataset cifar10 --ricap True
```
WideResNet28-10 +Random Erasing on CIFAR-10:
```
python train.py --dataset cifar10 --random-erase True
```
WideResNet28-10 +Mixup on CIFAR-10:
```
python train.py --dataset cifar10 --mixup True
```

## Results
| Model                           |    Error rate     |   Loss    | Error rate (paper) |
| :------------------------------ | :---------------: | :-------: | :----------------: |
| WideResNet28-10 baseline        |   3.82（96.18）   |   0.158   |        3.89        |
| WideResNet28-10 +RICAP          | **2.82（97.18）** |   0.141   |      **2.85**      |
| WideResNet28-10 +Random Erasing |   3.18（96.82）   | **0.114** |        4.65        |
| WideResNet28-10 +Mixup          |   3.02（96.98）   |   0.158   |        3.02        |



reimplementation

| Model                           |    Error rate     | Loss  | Error rate (paper) |
| :------------------------------ | :---------------: | :---: | :----------------: |
| WideResNet28-10 baseline        |   3.78（96.22）   |       |        3.89        |
| WideResNet28-10 +RICAP          | **2.81（97.19）** |       |      **2.85**      |
| WideResNet28-10 +Random Erasing |                   |       |        4.65        |
| WideResNet28-10 +Mixup          |   2.93（97.07）   | 0.158 |        3.02        |

