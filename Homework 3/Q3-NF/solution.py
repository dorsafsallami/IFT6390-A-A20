
import torch
import math
from torch import Tensor
from torch import nn
from typing import Tuple

from torch.distributions import MultivariateNormal

class PlanarTransformation(torch.nn.Module):
    """
    One layer of a planar flow. It can perform a planar transformation and
    return its log determinant (it also make sure the function is invertible
    by adjusting u in the case where uw^t < -1)
    """
    def __init__(self, dim: int = 2):
        super().__init__()
        self.u = torch.nn.Parameter(torch.normal(0, 0.01, (1, dim)))
        self.w = torch.nn.Parameter(torch.normal(0, 0.01, (1, dim)))
        self.b = torch.nn.Parameter(torch.zeros((1)))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply a planar transformation on x.
        :param x: the input, a tensor of size (batch_size, dim)
        :returns: the output, a tensor of size (batch_size, dim)
        """
        if torch.matmul(self.u, self.w.T) < -1:
            self.adjust_u()
        # 1. WRITE YOUR CODE HERE
        x_ =  x+self.u * torch.nn.Tanh()(torch.mm(x, self.w.T) + self.b)

        return x_

    def get_logdet(self, x: torch.Tensor, eps:float = 1e-8) -> torch.Tensor:
        """
        Calculate the log determinant of a planar tranformation on x
        :param x: the input, a tensor of size (batch_size, dim)
        :param eps: a small value used for numerical stability
        :returns: the output, a tensor of size (batch_size, 1)
        """
        if torch.mm(self.u, self.w.T) < -1:
            self.adjust_u()
        # 4. WRITE YOUR CODE HERE
        # det = ...

        a = torch.mm(x, self.w.T) + self.b
        psi = (1 - nn.Tanh()(a) ** 2) * self.w
        det = (1 + torch.mm(self.u, psi.T)).abs()
        t=torch.log(eps + det).reshape(-1,1)
        return t

    def adjust_u(self):
        """
        A function that adjust u to make sure the planar transformation is invertible
        """
        wu = torch.mm(self.u, self.w.T)
        m_wu = -1 + torch.log(1 + torch.exp(wu))
        self.u.data = self.u + torch.mm((m_wu - wu), self.w) / torch.norm(self.w, p=2, dim=1) ** 2


class Flow(torch.nn.Module):
    """
    A planar flow constituted of 'num_layers' planar transformations.
    Return the transformed data and the log determinant of the transformation.
    """
    def __init__(self, dim: int, num_layers: int):
        """
        :param dim: dimensionality of each transformation
        :param num_layers: total number of planar transformation
        """
        super().__init__()
        self.layers = torch.nn.ModuleList([PlanarTransformation(dim) for _ in range(num_layers)])

    def forward(self, x: torch.Tensor) -> [torch.Tensor, torch.Tensor]:
        """
        :param x: the input, a tensor of size (batch_size, dim)
        :returns: x, the transformed input and
                  logdet, the log determinant of the complete transformation
        """
        logdet = 0
        for layer in self.layers:
            # 3. WRITE YOUR CODE HERE
            logdet += layer.get_logdet(x)
            x= layer(x)
            # logdet = ...
            
        return x,logdet

def loss1(z0: torch.Tensor, logdet: torch.Tensor) -> torch.Tensor:
    """
    Calculate the negative likelihood of a normal (0,I) that has been transformed by a flow
    :param z0: a tensor of size (batch_size, dim)
    :param logdet: a tensor of size (batch_size, 1)
    :returns: the log likelihood for each z0, thus a tensor of size (batch_size, 1)
    """
    # 6. WRITE YOUR CODE HERE
    #log_q_k = base_dist.log_prob(z_0) - sum_log_det_jacob
    #forward(z0)
    nll =z0.mean(dim=1)
    print(nll)
    return nll.reshape(-1,1)


def loss2(target_density: torch.Tensor, z0: torch.Tensor, logdet: torch.Tensor) -> torch.Tensor:
    """
    Calculate the loss to train a flow where we don't use samples, but we have access to the target distribution
    :param target_density: a tensor of size (batch_size)
    :param z0: a tensor of size (batch_size, dim)
    :param logdet: a tensor of size (batch_size, 1)
    :returns: the log likelihood for each z0, thus a tensor of size (batch_size, 1)
    """
    # 8. WRITE YOUR CODE HERE
    
    loss = target_density-loss1(z0,logdet)
    # loss = ...
    base_log_prob = self.base_distr.log_prob(z0)
    target_density_log_prob = -self.distr(z)
    return (base_log_prob - target_density_log_prob - sum_log_det_J).mean()
    return loss



""" 
    def forward(self, x: torch.Tensor) -> [torch.Tensor, torch.Tensor]:

        logdet = 0
        for layer in self.layers:
            # 3. WRITE YOUR CODE HERE
            # logdet = ...
            
            pass
        return x,logdet"""

