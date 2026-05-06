# Minimal MNIST: Sparse Delta-State Attention 実験

## 実験目的
Recurrent-Depth 型の小型画像分類モデルで、各更新ステップの差分状態
\(\Delta h_t = h_t - h_{t-1}\) を利用する設計を比較する最小実験です。

この実験は **まず動くことを優先** した検証であり、SOTA性能や大規模再現は目的ではありません。

---

## モデル比較

### 1) baseline
- 4x4 patch 埋め込み + 小型 self-attention + FFN の単純モデル
- 差分状態は使用しない

### 2) delta_only
- hidden state を 4 ステップ再帰更新
- 各ステップで \(\Delta h\) を計算
- \(\Delta h\) から gate を生成し、update を調整

### 3) sparse_delta
- delta_only と同様に \(\Delta h\) を計算
- \(\Delta h\) を小型 SAE 風 encoder（Linear + ReLU）に通して sparse feature \(z\) を生成
- \(z\) から gate を生成し hidden update を調整
- 損失に L1 sparsity 項を追加:
  - `loss = cross_entropy + lambda_l1 * mean(|z|)`

---

## 共通設定（デフォルト）
- Dataset: `torchvision.datasets.MNIST`
- 入力: 28x28 を 4x4 patch に分割して token 列化
- Recurrent steps: 4
- Hidden dim: 128
- Batch size: 128
- Epochs: 3
- Optimizer: AdamW
- Seed 固定: 42
- Device: CUDA があれば使用、なければ CPU

---

## セットアップ

```bash
pip install -r requirements.txt
```

---

## 実行コマンド

```bash
python train.py --model_type baseline
python train.py --model_type delta_only
python train.py --model_type sparse_delta
```

必要に応じてエポック数などを上書きできます:

```bash
python train.py --model_type sparse_delta --epochs 5 --lambda_l1 1e-3
```

---

## 結果記録欄

| date | model_type | epochs | test_acc(%) | notes |
|---|---:|---:|---:|---|
| YYYY-MM-DD | baseline | 3 |  |  |
| YYYY-MM-DD | delta_only | 3 |  |  |
| YYYY-MM-DD | sparse_delta | 3 |  |  |

---

## 注意
- 本コードは「差分状態を使う再帰深度モデル」の最小検証用です。
- OpenMythos / Claude Mythos の再現ではありません。
- 複雑な抽象化を避け、`train.py` 1ファイルで追える構成にしています。
