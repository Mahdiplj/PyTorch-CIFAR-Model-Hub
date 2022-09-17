from lib.models.autorf import genotypes

from ..genotypes import *
from ..operations import *
from ..spaces import *
from .resnet20 import rf_resnet20

MODEL_LIST = {
    'resnet20': rf_resnet20,
}


def build_auto_network(model_name='resnet20', num_classes=10, genotype=None):
    return MODEL_LIST[model_name](num_classes=num_classes, genotype=genotype)
