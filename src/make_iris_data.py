# src/make_iris_data.py
from sklearn.datasets import load_iris
import pandas as pd
 
# Irisデータセットの読み込み
iris = load_iris()
 
# 特徴量とクラスをDataFrameに変換
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df['target'] = iris.target
 
# CSVファイルとして保存
csv_filename = 'raw_data.csv'
df.to_csv(csv_filename, index=False)
 
print(f"Irisデータセットを {csv_filename} として保存しました。")