import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import sys
import os
 
def process_data(input_file, output_file):
    # データを読み込む
    df = pd.read_csv(input_file)
 
    # 特徴量を選択（'target'列を除外）
    features = df.drop(columns=['target'])
 
    # MinMaxScalerのインスタンスを作成
    scaler = MinMaxScaler()
 
    # 特徴量を0から1の間にスケーリング
    scaled_features = scaler.fit_transform(features)
 
    # スケーリングしたデータで新しいデータフレームを作成
    scaled_df = pd.DataFrame(scaled_features, columns=features.columns)
 
    # 'target'列を追加
    scaled_df['target'] = df['target']
 
    # 出力ファイルのフォルダを作成（存在しない場合）
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
 
    # 結果をCSVファイルとして保存
    scaled_df.to_csv(output_file, index=False)
 
if __name__ == "__main__":
    # コマンドライン引数を取得
    if len(sys.argv) != 3:
        print("Usage: python xxx.py <input_file> <output_file>")
        sys.exit(1)
 
    input_file = sys.argv[1]
    output_file = sys.argv[2]
 
    # データ処理を実行
    process_data(input_file, output_file)