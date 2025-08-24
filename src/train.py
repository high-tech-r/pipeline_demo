import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import argparse
import json
from sklearn.metrics import accuracy_score, f1_score
import os
import matplotlib.pyplot as plt
 
# CSVファイルからデータを読み込む関数
def load_data(file_path):
    df = pd.read_csv(file_path)
    X = df.drop('target', axis=1).values
    y = df['target'].values
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)
 
# モデル定義
class IrisModel(nn.Module):
    def __init__(self):
        super(IrisModel, self).__init__()
        self.fc1 = nn.Linear(4, 10)
        self.fc2 = nn.Linear(10, 3)
 
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x
 
# トレーニング関数
def train_model(train_loader, val_loader, learning_rate, num_epochs):
    model = IrisModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
 
    epoch_metrics = []
 
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        train_loss /= len(train_loader.dataset)
 
        # バリデーション精度の計算
        model.eval()
        val_loss = 0
        correct = 0
        all_preds = []
        all_labels = []
        with torch.no_grad():
            for inputs, labels in val_loader:
                outputs = model(inputs)
                val_loss += criterion(outputs, labels).item()
                pred = outputs.argmax(dim=1)
                correct += pred.eq(labels).sum().item()
                all_preds.extend(pred.numpy())
                all_labels.extend(labels.numpy())
 
        val_loss /= len(val_loader.dataset)
        accuracy = correct / len(val_loader.dataset)
        f1 = f1_score(all_labels, all_preds, average='macro')
        
        epoch_metrics.append({
            'epoch': epoch+1, 
            'train_loss': train_loss, 
            'val_loss': val_loss,
            'accuracy': accuracy,
            'f1_score': f1
        })
 
        print(f'Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}, Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}')
 
    # エポックごとのメトリクスをCSVファイルに保存
    epoch_metrics_df = pd.DataFrame(epoch_metrics)
    os.makedirs('plot', exist_ok=True)
    epoch_metrics_df.to_csv('plot/epoch_metrics.csv', index=False)
 
    # 学習曲線のプロット
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epoch_metrics_df['epoch'], epoch_metrics_df['train_loss'], label='Train Loss')
    plt.plot(epoch_metrics_df['epoch'], epoch_metrics_df['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Learning Curve - Loss')
 
    plt.subplot(1, 2, 2)
    plt.plot(epoch_metrics_df['epoch'], epoch_metrics_df['accuracy'], label='Accuracy')
    plt.plot(epoch_metrics_df['epoch'], epoch_metrics_df['f1_score'], label='F1 Score')
    plt.xlabel('Epoch')
    plt.ylabel('Score')
    plt.legend()
    plt.title('Learning Curve - Metrics')
 
    plt.tight_layout()
    plt.savefig('plot/learning_curves.png')
 
    return model, train_loss, accuracy, f1
 
# メインスクリプト
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a deep learning model for Iris classification.')
    parser.add_argument('--learning_rate', type=float, required=True, help='Learning rate for training the model.')
    parser.add_argument('--num_epochs', type=int, required=True, help='Number of epochs for training the model.')
    parser.add_argument('--test_size', type=float, default=0.2, help='Proportion of the dataset to include in the test split.')
    args = parser.parse_args()
 
    # データを読み込む
    X, y = load_data('res/processed_data.csv')
 
    # データを訓練セットと検証セットに分割
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=args.test_size, random_state=42)
 
    # データローダーの作成
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
 
    # モデルをトレーニング
    model, final_train_loss, final_val_accuracy, final_val_f1 = train_model(
        train_loader, val_loader, args.learning_rate, args.num_epochs
    )
 
    # 学習済みモデルの保存
    os.makedirs('models', exist_ok=True)
    torch.save(model.state_dict(), 'models/iris_model.pkl')
 
    # 最終的な訓練セットと検証セットのロスと性能をJSONファイルに保存
    final_metrics = {
        'loss': final_train_loss,
        'acc': final_val_accuracy,
        'f1': final_val_f1,
        'learning_rate': args.learning_rate,
        'num_epochs': args.num_epochs,
        'test_size': args.test_size
    }
    os.makedirs('metrics', exist_ok=True)
    with open('metrics/iris_metrics.json', 'w') as f:
        json.dump(final_metrics, f)
 
    print("Training completed. Model and metrics saved.")