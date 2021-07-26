import torch
import torch.nn as nn


class NeuralNet(nn.Module):
    """
    A Neural network class defined by inheriting from the base class nn.Module
    Here we use Linear function which Applies a linear transformation to the incoming data
    There are 4 class members: l1 is an input layer, l2 is a hidden layer, l3 in an output layer, and
    relu is an activation function
    """
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size) 
        self.l2 = nn.Linear(hidden_size, hidden_size) 
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        """ 
        Define how the model is going to run from input to output.
        """
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        # no activation and no softmax at the end
        return out