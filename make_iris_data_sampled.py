# src/make_iris_data_sampled.py
from sklearn.datasets import load_iris
import pandas as pd
 
# Irisデータセットの読み込み
iris = load_iris()
 
# 特徴量とクラスをDataFrameに変換
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df['target'] = iris.target
 
# 各クラスから50%をサンプリング
sampled_df = df.groupby('target').sample(frac=0.5, random_state=42)
 
# CSVファイルとして保存
csv_filename = 'sampled_iris_data.csv'
sampled_df.to_csv(csv_filename, index=False)
print(f"Irisデータセットを {csv_filename} として保存しました。")
print(f"サンプリング後のデータ数: {len(sampled_df)}")