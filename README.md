
# akari_smile_counter  

## セットアップ方法  
1.プログラムをインストール後、ディレクトリを開く  
cd akari_smile_counter  

2.ディレクトリを移動後以下のコマンドで仮想環境を有効化する。  
source venv/bin/activate  

3.サブモジュールの初期化と更新  
git submodule update --init  

4.必要なパッケージをインストール  
pip install -r requirements.txt  

5.インストールの確認は以下のコマンドを使う  
pip show depthai-sdk  

## 起動方法  
1.アプリケーションの実行は以下のコマンドで行う  
python3 main.py  

2.プログラムの終了:q  

3.カウントダウンのリセット:r  

## その他  
このアプリケーションは愛知工業大学 情報科学部 知的制御研究室により作成されたものです。  
