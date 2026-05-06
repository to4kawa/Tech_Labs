import argparse
import random
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


class PatchEmbed(nn.Module):
    def __init__(self, patch_size: int = 4, hidden_dim: int = 128):
        super().__init__()
        self.patch_size = patch_size
        self.unfold = nn.Unfold(kernel_size=patch_size, stride=patch_size)
        patch_dim = patch_size * patch_size
        self.proj = nn.Linear(patch_dim, hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, 1, 28, 28]
        patches = self.unfold(x)  # [B, patch_dim, num_patches]
        patches = patches.transpose(1, 2)  # [B, num_patches, patch_dim]
        return self.proj(patches)  # [B, num_patches, hidden_dim]


class BaselineModel(nn.Module):
    def __init__(self, hidden_dim: int = 128, num_classes: int = 10):
        super().__init__()
        self.embed = PatchEmbed(patch_size=4, hidden_dim=hidden_dim)
        self.attn = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=4, batch_first=True)
        self.ffn = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim * 2),
            nn.GELU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
        )
        self.cls = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor):
        h = self.embed(x)
        attn_out, _ = self.attn(h, h, h)
        h = h + attn_out
        h = h + self.ffn(h)
        pooled = h.mean(dim=1)
        logits = self.cls(pooled)
        return logits, None


class DeltaOnlyModel(nn.Module):
    def __init__(self, hidden_dim: int = 128, steps: int = 4, num_classes: int = 10):
        super().__init__()
        self.steps = steps
        self.embed = PatchEmbed(patch_size=4, hidden_dim=hidden_dim)
        self.delta_to_gate = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Sigmoid(),
        )
        self.update = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.cls = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor):
        h = self.embed(x)
        prev_h = h
        for _ in range(self.steps):
            delta = h - prev_h
            gate = self.delta_to_gate(delta)
            update = self.update(h)
            prev_h = h
            h = h + gate * update
        pooled = h.mean(dim=1)
        logits = self.cls(pooled)
        return logits, None


class SparseDeltaModel(nn.Module):
    def __init__(self, hidden_dim: int = 128, sparse_dim: int = 64, steps: int = 4, num_classes: int = 10):
        super().__init__()
        self.steps = steps
        self.embed = PatchEmbed(patch_size=4, hidden_dim=hidden_dim)
        self.encoder = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, sparse_dim),
            nn.ReLU(),
        )
        self.z_to_gate = nn.Sequential(
            nn.Linear(sparse_dim, hidden_dim),
            nn.Sigmoid(),
        )
        self.update = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.cls = nn.Linear(hidden_dim, num_classes)

    def forward(self, x: torch.Tensor):
        h = self.embed(x)
        prev_h = h
        z_l1_terms = []
        for _ in range(self.steps):
            delta = h - prev_h
            z = self.encoder(delta)
            gate = self.z_to_gate(z)
            update = self.update(h)
            prev_h = h
            h = h + gate * update
            z_l1_terms.append(z.abs().mean())
        pooled = h.mean(dim=1)
        logits = self.cls(pooled)
        l1_loss = torch.stack(z_l1_terms).mean()
        return logits, l1_loss


@dataclass
class TrainConfig:
    model_type: str
    batch_size: int = 128
    epochs: int = 3
    lr: float = 1e-3
    weight_decay: float = 1e-4
    hidden_dim: int = 128
    steps: int = 4
    lambda_l1: float = 1e-3
    seed: int = 42


def build_model(cfg: TrainConfig) -> nn.Module:
    if cfg.model_type == "baseline":
        return BaselineModel(hidden_dim=cfg.hidden_dim)
    if cfg.model_type == "delta_only":
        return DeltaOnlyModel(hidden_dim=cfg.hidden_dim, steps=cfg.steps)
    if cfg.model_type == "sparse_delta":
        return SparseDeltaModel(hidden_dim=cfg.hidden_dim, steps=cfg.steps)
    raise ValueError(f"Unknown model_type: {cfg.model_type}")


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            logits, _ = model(images)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return 100.0 * correct / total


def train(cfg: TrainConfig) -> None:
    set_seed(cfg.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    transform = transforms.ToTensor()
    train_ds = datasets.MNIST(root="./data", train=True, transform=transform, download=True)
    test_ds = datasets.MNIST(root="./data", train=False, transform=transform, download=True)

    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=2)

    model = build_model(cfg).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

    for epoch in range(1, cfg.epochs + 1):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            logits, l1_term = model(images)
            ce_loss = F.cross_entropy(logits, labels)
            loss = ce_loss
            if cfg.model_type == "sparse_delta" and l1_term is not None:
                loss = loss + cfg.lambda_l1 * l1_term
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * labels.size(0)

        avg_loss = running_loss / len(train_loader.dataset)
        acc = evaluate(model, test_loader, device)
        print(f"Epoch {epoch:02d}/{cfg.epochs} | train_loss={avg_loss:.4f} | test_acc={acc:.2f}%")


def parse_args() -> TrainConfig:
    parser = argparse.ArgumentParser(description="Minimal MNIST experiment for delta-state attention variants")
    parser.add_argument("--model_type", type=str, required=True, choices=["baseline", "delta_only", "sparse_delta"])
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight_decay", type=float, default=1e-4)
    parser.add_argument("--hidden_dim", type=int, default=128)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--lambda_l1", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    return TrainConfig(**vars(args))


if __name__ == "__main__":
    config = parse_args()
    train(config)
