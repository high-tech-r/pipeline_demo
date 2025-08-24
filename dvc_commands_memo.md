# DVC よく使うコマンドメモ

## 初期化

- `dvc init` : DVCをリポジトリに初期化
- `dvc remote add -d myremote s3://bucket/path` : リモートストレージを追加

## データ管理

- `dvc add data.csv` : データファイルをDVCで管理対象に追加
- `git add data.csv.dvc .gitignore` : Gitに追跡ファイルを追加
- `git commit -m "Add data.csv to DVC"`

## リモート同期

- `dvc push` : DVCキャッシュからリモートストレージへアップロード
- `dvc pull` : リモートストレージからデータを取得
- `dvc fetch` : データを取得（作業ディレクトリには展開しない）

## パイプライン管理

⚠️ **変数展開エラーについて**

DVCの `dvc stage add` では `${var}` のような変数参照は、`dvc.yaml` 内の `params.yaml` と紐づけないとエラーになります。例えば以下のように書きます。

### params.yaml
```yaml
lr: 0.01
train:
  epochs: 100
  test_size: 0.2
```

### dvc.yaml の例
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
      - plot/epoch_metrics.csv
      - plot/learning_curves.png
    params:
      - lr
      - train.epochs
      - train.test_size
```

### よく使う関連コマンド
- `dvc params diff` : params.yaml の差分を確認
- `dvc repro` : params.yaml を更新した後に再実行

---

- `dvc run -n stage_name -d input.csv -o output.csv python script.py` : ステージを作成（旧形式）
- `dvc stage add -n stage_name -d input.csv -o output.csv python script.py` : ステージを追加（新推奨コマンド）
- `dvc repro` : パイプラインを再実行
- `dvc dag` : パイプライン依存関係を表示

## 状態確認

- `dvc status` : ワークスペースとキャッシュ/リモートの状態確認
- `dvc diff` : 過去のバージョンとの違いを比較
- `dvc metrics show` : 指標値の確認

## プロット可視化

- `dvc plots show plot/epoch_metrics.csv` : 学習曲線などのプロットを確認
- `dvc plots diff` : 過去の実験との可視化比較
- `dvc plots templates` : 利用可能なテンプレートを確認
  - `-t confusion` : 混同行列を可視化
  - `-t scatter` : 散布図を可視化
  - `-t simple` : 単純な折れ線・棒グラフを可視化
  - `-t linear` : 線形プロット
  - `--x <col>` : 横軸に使うカラムを指定
  - `--y <col>` : 縦軸に使うカラムを指定（複数可: `--y loss,val_loss`）
  - `--targets <file>` : 可視化対象のファイルを指定

### よく使うコマンド例

- 学習曲線（epoch を横軸、loss/val\_loss を縦軸）
  ```bash
  dvc plots show plot/epoch_metrics.csv -t simple -x epoch -y loss,val_loss
  ```
- 実験比較（前コミットとの差分を重ねて確認）
  ```bash
  dvc plots diff -t simple -x epoch -y loss,val_loss
  ```
- 混同行列（`classes.csv` に `target,predicted` 列がある想定）
  ```bash
  dvc plots show -t confusion --targets plot/classes.csv -x predicted -y target
  # 直近コミットとの差
  dvc plots diff -t confusion --targets plot/classes.csv -x predicted -y target
  ```
- 散布図（予測値と実測値の相関）
  ```bash
  dvc plots show -t scatter --targets plot/preds_vs_true.csv -x true -y pred
  ```

### `dvc.yaml` に設定を記録する（`dvc plots modify`）

`dvc plots modify` を使うと、可視化のメタ情報（x/y、テンプレート、タイトル等）を `dvc.yaml` に保存できます。

```bash
# epoch_metrics.csv のx/yやテンプレート、タイトルを記録
 dvc plots modify plot/epoch_metrics.csv -x epoch --y loss,val_loss \
   --template simple --title "Learning Curves"

# 混同行列の設定を記録
 dvc plots modify plot/classes.csv -t confusion -x predicted -y target \
   --title "Confusion Matrix"
```

上記を実行すると `dvc.yaml` の `plots:` セクションに反映されます（手書きでもOK）。

### `dvc.yaml` のサンプル

```yaml
stages:
  train:
    cmd: python src/train.py --learning_rate 0.01 --num_epochs 100 --test_size 0.2
    deps:
      - res/processed_data.csv
      - src/train.py
    outs:
      - models/iris_model.pkl
    metrics:
      - metrics/iris_metrics.json
    plots:
      # 学習曲線（epochをx、loss/val_lossをy）
      - plot/epoch_metrics.csv:
          x: epoch
          y:
            - loss
            - val_loss
          template: simple
          title: Learning Curves
      # 混同行列（target vs predicted）
      - plot/classes.csv:
          template: confusion
          x: predicted
          y: target
          title: Confusion Matrix
```

> メモ
>
> - `plots:` で宣言したファイルは Git に追跡されます（中身は生成物でもOK）。
> - CSVヘッダ名と `x`/`y` の対応が重要です。列名が違う場合は `dvc plots modify` で合わせるか、CSVを前処理してください。
> - `dvc plots show --open` でブラウザ表示も可能です（環境により挙動が異なることがあります）。

## キャッシュとクリーンアップ

- `dvc gc` : 不要なキャッシュの削除
- `dvc remove data.csv.dvc` : データを管理対象から外す

## バージョン管理

- `git checkout <branch>` : Gitブランチ切り替えでデータバージョンも切り替え
- `dvc checkout` : DVCの管理ファイルに従ってデータを更新

