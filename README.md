# 【2025年版】DVCで実現するMLOps実践ガイド【Python, DVC】

本リポジトリは、Udemy 講座\
**「【2025年版】DVCで実現するMLOps実践ガイド【Python, DVC】」**\
から学んだ内容を実践した際の記録です。

---

## 📌 学習背景と目的

- 機械学習の実務では **実験の再現性・追跡性・共有性** が重要。
- 従来の「ファイルコピー」や「Excel管理」では限界があるため、\
  **DVC + Git による実験管理とMLOps基盤** を導入。
- 転職活動に向けて、**実務的に使えるスキルを証明する成果物** として公開。

---

## 🚀 このリポジトリで実践していること

1. **データとコードの分離管理**

   - `dvc add` でデータを Git 管理から切り離し、ストレージに保存。
   - バージョンごとにデータを追跡可能。

2. **実験の自動再現 (dvc.yaml)**

   - 学習パイプラインを `dvc.yaml` に定義。
   - `dvc repro` で誰でも同じ実験を再実行可能。

3. **ハイパーパラメータ管理 (params.yaml)**

   - `params.yaml` に学習率やエポック数を記録。
   - `dvc exp run` で異なるパラメータをキューに積み、一括実行。
   - 実験差分を `dvc exp show` / `dvc exp diff` で比較。

4. **可視化とレポート**

   - `dvc plots` により、学習曲線や混同行列を可視化。
   - `dvc metrics show` で精度・F1スコアなどを定量比較。

---

## 📂 ディレクトリ構成（例）

```
.
├─ src/                 # 学習スクリプト
├─ data/                # 入力データ
├─ metrics/             # 精度/F1スコアなど
├─ plot/                # 学習曲線・混同行列
├─ params.yaml          # ハイパラ管理
├─ dvc.yaml             # パイプライン定義
└─ README.md            # 本ドキュメント
```

---

## 🛠️ 主要コマンド例

```bash
# データをDVC管理に追加
dvc add data/dataset.csv
git add data/dataset.csv.dvc .gitignore
git commit -m "Add dataset with DVC"

# 実験をキューに追加
dvc exp run --queue --name lr_001_ep100
dvc exp run --queue --name lr_005_ep200

# キューを一括実行
dvc exp run --run-all

# 実験結果を一覧表示
dvc exp show --all-commits

# プロット比較（学習曲線）
dvc plots diff -t simple -x epoch -y loss -y val_loss --targets plot/epoch_metrics.csv
```

---

## 🌟 アピールポイント

- **MLOps基盤を自分の手で再現**\
  → 実験追跡・再現性・チーム共有のフローを構築済み。
- **DVC + Git によるデータバージョニング** を理解し、\
  研究レベルから実務レベルへの応用経験あり。
- **実験自動化 / 可視化 / CI/CD 連携** へ拡張可能なベースを習得済み。

---

## 🎯 今後の展望

- CI/CD（GitHub Actions）と連携した自動学習パイプライン
- Docker / Kubernetes 上での分散実行
- MLflow や Weights & Biases との統合

---

## 📖 参考

- Udemy: [【2025年版】DVCで実現するMLOps実践ガイド【Python, DVC】](https://www.udemy.com/)
- DVC公式ドキュメント: [https://dvc.org/doc](https://dvc.org/doc)

