"""Convolutional AutoEncoder for anomaly detection."""

from __future__ import annotations

import torch
import torch.nn as nn


class ConvBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, stride=2, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class DeconvBlock(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.ConvTranspose2d(in_ch, out_ch, 4, stride=2, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class AutoEncoder(nn.Module):
    """224x224 RGB → latent → 224x224 reconstruction."""

    def __init__(self, latent_dim: int = 128):
        super().__init__()
        self.encoder = nn.Sequential(
            ConvBlock(3, 32),    # 112
            ConvBlock(32, 64),   # 56
            ConvBlock(64, 128),  # 28
            ConvBlock(128, 256), # 14
            ConvBlock(256, 512), # 7
        )
        self.fc_enc = nn.Linear(512 * 7 * 7, latent_dim)
        self.fc_dec = nn.Linear(latent_dim, 512 * 7 * 7)
        self.decoder = nn.Sequential(
            DeconvBlock(512, 256),  # 14
            DeconvBlock(256, 128),  # 28
            DeconvBlock(128, 64),   # 56
            DeconvBlock(64, 32),    # 112
            nn.ConvTranspose2d(32, 3, 4, stride=2, padding=1),  # 224
            nn.Sigmoid(),
        )

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        h = self.encoder(x).flatten(1)
        return self.fc_enc(h)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        h = self.fc_dec(z).view(-1, 512, 7, 7)
        return self.decoder(h)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encode(x)
        recon = self.decode(z)
        return recon, z

    @staticmethod
    def reconstruction_error(x: torch.Tensor, recon: torch.Tensor) -> torch.Tensor:
        """Per-sample MSE (batch,)."""
        err = (x - recon).pow(2).flatten(1).mean(dim=1)
        return err
