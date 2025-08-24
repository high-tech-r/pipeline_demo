# DVC 実験運用ガイド：`exp run` / `exp queue` とブランチ比較（test1〜test3）

> 目的：`params.yaml` でハイパラを変えながら、`test1`/`test2`/`test3` 各ブランチで実験をキュー投入・一括実行し、指標やプロットを横断比較できる運用を最短で構築する。

---

## 0) 前提レイアウト（例）

```
.
├─ dvc.yaml            # stages: train（metrics, plots を出力）
├─ params.yaml         # lr, train.epochs などのハイパラ
├─ src/train.py        # params を読み込んで学習
├─ metrics/iris_metrics.json   # {"acc": 0.93, "f1": 0.90, ...}
└─ plot/epoch_metrics.csv      # epoch,loss,val_loss
```

---

## 1) 比較用の Git ブランチを作成

```bash
# ベースは main とする例
git checkout -b test1
# 変更コミット後
git checkout -b test2 main
# 変更コミット後
git checkout -b test3 main
```

> 同時並行で走らせる場合は \`\` を使うと便利（別ディレクトリで test1/2/3 を同時実行可能）。

```bash
# 例：同一リポジトリを 3 つの作業ディレクトリで運用
mkdir ../wt && cd ../wt
git worktree add ../proj_test1 test1
git worktree add ../proj_test2 test2
git worktree add ../proj_test3 test3
```

---

## 2) 各ブランチでパラメータを差し替える

`params.yaml` をそれぞれのブランチで編集（例）

- test1

```yaml
lr: 0.01
train:
  epochs: 100
  test_size: 0.2
```

- test2

```yaml
lr: 0.02
train:
  epochs: 120
  test_size: 0.2
```

- test3

```yaml
lr: 0.005
train:
  epochs: 100
  test_size: 0.25
```

> 変更を Git にコミットしておくと、後の比較で混乱しない。

```bash
git add params.yaml
git commit -m "tune params for this branch"
```

---

## 3) 実験をキューに積む（`dvc exp run --queue`）

### 単一作業ディレクトリでブランチを順番に切り替えてキュー積み

```bash
# test1 で
git switch test1
# 追加で複数バリアント積む例（名前を付けると後でわかりやすい）
dvc exp run --queue --name t1_lr001_ep100

# test2 で
git switch test2
dvc exp run --queue --name t2_lr002_ep120

# test3 で
git switch test3
dvc exp run --queue --name t3_lr0005_ep100_ts025
```

> ポイント：`--queue` は **現ブランチの HEAD** に紐づいた実験をキューへ登録する。ブランチを切り替えて同様に積むことで、**ブランチ別の実験** を同一キューに混在させられる。

### worktree で並行環境から積む場合

それぞれの worktree ディレクトリ（`proj_test1`, `proj_test2`, `proj_test3`）で同様に `dvc exp run --queue` を実行すれば OK。

---

## 4) キューを一括実行（`dvc exp run --run-all`）

```bash
# どのディレクトリからでも（同一リポ配下なら）
dvc exp run --run-all
```

> ランナーが順番に実行する。マシン性能に応じて並列度を上げたい場合は `--jobs N` も検討。

---

## 5) 実験結果の一覧・比較

### 表形式で俯瞰（`exp show`）

```bash
# 現在のブランチのみ
dvc exp show

# ブランチ跨ぎで俯瞰（直近のコミット由来の実験も含む）
dvc exp show --all-commits
# あるいはブランチを明示
# （DVC 2.x/3.x では --all-branches/--all-commits の挙動差があるため、まず --all-commits を推奨）
```

> 列に `params.yaml` の値や `metrics/*.json` が並ぶ。CSV で保存するなら：

```bash
dvc exp show --all-commits --csv > exp_table.csv
```

### 差分（`exp diff`）

```bash
# 直近実験 vs ベースライン
dvc exp diff

# 任意の 2 つの実験/コミットを比較（ID/ブランチ/HEAD 等で指定）
dvc exp diff test1~1 t3_lr0005_ep100_ts025
# 例：ブランチの HEAD 同士
dvc exp diff test1 test2
```

> 指標（metrics）とパラメータ差分がまとまって表示される。

### プロット比較（plots）

`dvc.yaml` の `plots:` を設定していれば、実験 ID／ブランチを指定して重ね描画できる。

```bash
# ブランチ HEAD の学習曲線を比較（x=epoch, y=loss/val_loss）
dvc plots diff -t simple -x epoch -y loss --targets plot/epoch_metrics.csv test1 test2 test3
# val_loss も見る場合は -y を繰り返し
dvc plots diff -t simple -x epoch -y loss -y val_loss --targets plot/epoch_metrics.csv test1 test2 test3
```

> UI で見たい場合は `--open` を付ける。

---

## 6) よく使う運用コマンド

- **キューの一覧を確認**

  ```bash
  dvc exp show
  ```

  → 現在待機している実験キューのリストを表示する。

- **実験に名前を付ける**

  ```bash
  dvc exp run --queue --name t1_tryA
  ```

- **実験の適用（ワークスペースに反映）**

  ```bash
  dvc exp apply <exp-id-or-name>
  ```

- **実験を通常の Git ブランチ化**（共有したい結果を昇格）

  ```bash
  dvc exp branch <exp-id-or-name> feature/best-exp
  ```

- **実験の保存（コミットとして取り込み）**

  ```bash
  dvc exp save   # 生成物（dvc.lock/metrics 等）を通常コミット化
  ```

- **実験のバックアップ/共有**

  ```bash
  # Git リモートへ実験を push/pull（メタデータ）
  dvc exp push origin <exp-id-or-name>
  dvc exp pull origin <exp-id-or-name>
  ```

---

## 7) つまずきポイントと対策

- **params が反映されない**：`dvc.yaml` の `stages.<name>.params:` に参照キーを列挙（例：`- lr`, `- train.epochs`）。
- **plots の y を複数指定**：`-y` を繰り返し指定（`-y loss -y val_loss`）。
- **ブランチ跨ぎの比較が出ない**：`dvc exp show --all-commits` で俯瞰、`dvc exp diff <rev1> <rev2>` で明示比較。
- **並行実行したい**：`git worktree` でブランチ毎に別ディレクトリを作るか、`dvc exp run --run-all --jobs N` を利用。

---

## 8) 最小ワンライナー集（コピペ用）

```bash
# キュー投入（ブランチごと）
git switch test1 && dvc exp run --queue --name t1
git switch test2 && dvc exp run --queue --name t2
git switch test3 && dvc exp run --queue --name t3

# 一括実行
dvc exp run --run-all

# 一覧・CSV
dvc exp show --all-commits
dvc exp show --all-commits --csv > exp.csv

# 差分（ブランチ間）
dvc exp diff test1 test3

# プロット比較（学習曲線）
dvc plots diff -t simple -x epoch -y loss -y val_loss --targets plot/epoch_metrics.csv test1 test2 test3
```

---

### 補足：`dvc.yaml` 抜粋（参考）

```yaml
stages:
  train:
    cmd: python src/train.py --learning_rate ${lr} --num_epochs ${train.epochs} --test_size ${train.test_size}
    deps:
      - res/processed_data.csv
      - src/train.py
    outs:
      - models/iris_model.pkl
    metrics:
      - metrics/iris_metrics.json
    plots:
      - plot/epoch_metrics.csv:
          x: epoch
          y: [loss, val_loss]
          template: simple
          title: Learning Curves
    params:
      - lr
      - train.epochs
      - train.test_size
```

> 必要なら `confusion` テンプレート等も `plots:` に追加しておくと `exp diff` と併用しやすい。

