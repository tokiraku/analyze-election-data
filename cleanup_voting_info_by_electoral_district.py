import pandas as pd
import os

def is_header_or_unwanted_row(row_data):
    """
    行がヘッダーや不要な行かどうかを判定する関数
    """
    # 行データを文字列に変換してチェック
    row_str = ' '.join([str(val) for val in row_data if pd.notna(val)])
    
    # タイトル行のパターン
    title_patterns = [
        '参議院議員選挙',
        '選出議員選挙',
        '候補者別得票調べ',
        '開票結果調べ',
        '市区町村別',
        '選挙管理委員会',
        '執行',
        '投票情報'
    ]
    
    # ヘッダー行のパターン
    header_patterns = [
        '候補者名',
        '政党名',
        '市区町村',
        '得票数',
        '得票総数',
        '投票率',
        '当選人',
        '届出番号',
        'かりがね',
        'コメント',
        '結果',
        '投票所',
        '有権者数'
    ]
    
    # 単位や説明行のパターン
    unit_patterns = [
        '（票）',
        '（％）',
        '（人）',
        '計',
        'Unnamed'
    ]
    
    # パターンマッチング
    for pattern in title_patterns + header_patterns + unit_patterns:
        if pattern in row_str:
            return True
    
    return False

def is_header_text(text):
    """
    テキストがヘッダーや不要なテキストかどうかを判定する関数
    """
    if pd.isna(text):
        return False
    
    text_str = str(text).strip()
    
    # 明らかにヘッダーと思われるキーワード
    header_keywords = [
        '選挙',
        '候補者',
        '政党',
        '得票',
        '投票',
        '開票',
        '結果',
        '調べ',
        '一覧',
        '市区町村',
        '管理委員会',
        '執行',
        'かりがね',
        '投票所',
        '有権者'
    ]
    
    for keyword in header_keywords:
        if keyword in text_str:
            return True
    
    return False

def load_excel_sheets():
    """
    埼玉投票情報_選挙区.xlsファイルの全シートを確認し、指定されたシートを読み込む関数
    """
    # ファイルパスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "埼玉投票情報_選挙区.xls")
    
    try:
        # まず、利用可能なシート名を確認
        print(f"ファイルを読み込み中: {file_path}")
        excel_file = pd.ExcelFile(file_path, engine='xlrd')
        print(f"利用可能なシート: {excel_file.sheet_names}")
        
        # 全シートを処理対象とする
        target_sheets = excel_file.sheet_names
        print(f"処理対象のシート: {target_sheets}")
        
        sheet_data = {}
        
        for sheet_name in target_sheets:
            if sheet_name:
                print(f"\nシート '{sheet_name}' を読み込み中...")
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                sheet_data[sheet_name] = df
                print(f"データの形状: {df.shape}")
                print(f"列名: {list(df.columns)}")
                print(f"データの先頭3行:")
                print(df.head(3))
            else:
                print(f"警告: 空のシート名が見つかりました。")
        
        return sheet_data
        
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def clean_and_save_sheet_data(sheet_data, sheet_name):
    """
    シートデータをクリーンアップしてCSVに保存する関数
    """
    if sheet_data is None or sheet_data.empty:
        print(f"データが空です: {sheet_name}")
        return
    
    print(f"\n--- {sheet_name} のデータクリーンアップ開始 ---")
    
    # データのコピーを作成
    df = sheet_data.copy()
    
    # 空の行を削除
    df = df.dropna(how='all')
    
    # 空の列を削除
    df = df.dropna(axis=1, how='all')
    
    # 列名の先頭・末尾の空白を削除
    df.columns = df.columns.astype(str).str.strip()
    
    # 無名の列（Unnamed:で始まる列）で内容が空の列を削除
    unnamed_cols = [col for col in df.columns if 'Unnamed:' in str(col)]
    for col in unnamed_cols:
        if df[col].isna().all() or (df[col].astype(str).str.strip() == '').all():
            df = df.drop(col, axis=1)
    
    # データの先頭に不要な情報行がある場合の処理
    # 最初の数行をチェックして、実際のデータ開始行を見つける
    data_start_row = 0
    for i in range(min(10, len(df))):
        # 数値データまたは候補者名などの実際のデータが含まれている行を探す
        row_data = df.iloc[i].astype(str).str.strip()
        non_empty_count = sum(1 for val in row_data if val not in ['', 'nan', 'NaN'])
        if non_empty_count >= len(df.columns) * 0.3:  # 30%以上の列にデータがある行
            data_start_row = i
            break
    
    if data_start_row > 0:
        df = df.iloc[data_start_row:].reset_index(drop=True)
        print(f"不要な上部の{data_start_row}行を削除しました")
    
    # ヘッダー行や不要な行をフィルタリング
    print("ヘッダー行と不要な行をフィルタリング中...")
    original_rows = len(df)
    
    # 各行をチェックしてヘッダーや不要な行を除外
    mask = []
    for index, row in df.iterrows():
        is_unwanted = is_header_or_unwanted_row(row.values)
        mask.append(not is_unwanted)
    
    df = df[mask].reset_index(drop=True)
    filtered_rows = original_rows - len(df)
    
    if filtered_rows > 0:
        print(f"🔄 ヘッダー行/不要な行を除外: {filtered_rows}行")
    else:
        print("✓ フィルタリング対象の行は見つかりませんでした")
    
    # 文字列データの前後の空白を削除
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', '')
    
    # tmpディレクトリを作成してクリーンアップ前のデータを保存
    tmp_dir = "tmp_info"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    tmp_filename = os.path.join(tmp_dir, f"選挙区_{sheet_name}_クリーンアップ前.csv")
    df.to_csv(tmp_filename, index=False, encoding='utf-8-sig')
    print(f"📁 クリーンアップ前データを保存: {tmp_filename}")
    
    # 重複行を削除
    original_rows = len(df)
    df = df.drop_duplicates()
    removed_duplicates = original_rows - len(df)
    if removed_duplicates > 0:
        print(f"🔄 重複行を削除: {removed_duplicates}行")
    else:
        print("✓ 重複行は見つかりませんでした")
    
    # 重複する列名がある場合の処理
    duplicate_cols = []
    unique_cols = []
    col_counts = {}
    
    for col in df.columns:
        if col in col_counts:
            col_counts[col] += 1
            new_col_name = f"{col}_{col_counts[col]}"
            duplicate_cols.append((col, new_col_name))
            unique_cols.append(new_col_name)
        else:
            col_counts[col] = 1
            unique_cols.append(col)
    
    if duplicate_cols:
        df.columns = unique_cols
        print(f"🔄 重複する列名を修正: {len(duplicate_cols)}個")
        for old_name, new_name in duplicate_cols:
            print(f"   '{old_name}' → '{new_name}'")
    
    print(f"クリーンアップ後のデータ形状: {df.shape}")
    print(f"クリーンアップ後の列名: {list(df.columns)}")
    
    # 列名を意味のある名前に変更
    if len(df.columns) >= 19:
        column_mapping = {
            df.columns[0]: "市区町村名",
            df.columns[1]: "男性有権者数",
            df.columns[2]: "女性有権者数", 
            df.columns[3]: "有権者数計",
            df.columns[4]: "男性投票者数",
            df.columns[5]: "女性投票者数",
            df.columns[6]: "投票者数計",
            df.columns[7]: "男性期日前投票者数",
            df.columns[8]: "女性期日前投票者数",
            df.columns[9]: "期日前投票者数計",
            df.columns[10]: "男性投票率",
            df.columns[11]: "女性投票率",
            df.columns[12]: "投票率計",
            df.columns[13]: "順位",
            df.columns[14]: "男性期日前投票率",
            df.columns[15]: "女性期日前投票率",
            df.columns[16]: "期日前投票率計",
            df.columns[17]: "確定時刻_時",
            df.columns[18]: "確定時刻_分"
        }
        
        df = df.rename(columns=column_mapping)
        print("✅ 列名を意味のある名前に変更しました")
        print(f"変更後の列名: {list(df.columns)}")
    
    # outputディレクトリを作成して最終結果を保存
    output_dir = "output_info"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    csv_filename = os.path.join(output_dir, f"選挙区_{sheet_name}_最終版.csv")
    
    # CSVファイルとして保存
    try:
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"✓ 最終CSVファイルを保存しました: {csv_filename}")
        
        # 保存したデータの概要を表示
        print(f"保存されたデータの先頭5行:")
        print(df.head())
        
    except Exception as e:
        print(f"CSVファイルの保存中にエラーが発生しました: {e}")
    
    return df

def analyze_voting_info_data(df):
    """
    投票情報データの基本的な分析を行う関数
    """
    if df is None or df.empty:
        return
    
    print("\n--- データの基本情報 ---")
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    
    # データの重複状況を確認
    total_rows = len(df)
    unique_rows = len(df.drop_duplicates())
    duplicate_rows = total_rows - unique_rows
    
    print(f"ユニークな行数: {unique_rows}")
    if duplicate_rows > 0:
        print(f"⚠️  重複していた行数: {duplicate_rows}")
        print(f"重複率: {duplicate_rows/total_rows*100:.2f}%")
    else:
        print("✓ 重複は完全に除去されています")
    
    print(f"欠損値の数:")
    missing_data = df.isnull().sum()
    for col, missing_count in missing_data.items():
        if missing_count > 0:
            print(f"  {col}: {missing_count}個 ({missing_count/len(df)*100:.2f}%)")
    
    if missing_data.sum() == 0:
        print("  欠損値はありません ✓")
    
    # 数値列のみの統計情報を表示
    numeric_columns = df.select_dtypes(include=['number']).columns
    if len(numeric_columns) > 0:
        print(f"\n--- 数値データの統計情報 (数値列: {len(numeric_columns)}個) ---")
        print(df[numeric_columns].describe())
    else:
        print("\n--- 数値列が見つかりませんでした ---")
    
    # 文字列列の情報を表示
    text_columns = df.select_dtypes(include=['object']).columns
    if len(text_columns) > 0:
        print(f"\n--- テキストデータの情報 (文字列列: {len(text_columns)}個) ---")
        for col in text_columns[:5]:  # 最初の5列のみ表示
            unique_values = df[col].nunique()
            print(f"  {col}: {unique_values}種類の値")
            if unique_values <= 10:  # 10種類以下の場合は値も表示
                print(f"    値: {list(df[col].unique())}")

def create_summary_report(all_processed_data):
    """
    全体のサマリーレポートを作成する関数
    """
    print(f"\n{'='*60}")
    print("📊 投票情報処理結果サマリーレポート（選挙区版）")
    print(f"{'='*60}")
    
    output_dir = "output_info"
    summary_file = os.path.join(output_dir, "選挙区_投票情報処理サマリーレポート.txt")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("埼玉投票情報分析（選挙区版） - 処理サマリーレポート\n")
        f.write(f"処理日時: {pd.Timestamp.now()}\n")
        f.write("="*60 + "\n\n")
        
        for sheet_name, df in all_processed_data.items():
            if df is not None:
                f.write(f"シート: {sheet_name}\n")
                f.write(f"  - 最終行数: {len(df)}\n")
                f.write(f"  - 列数: {len(df.columns)}\n")
                f.write(f"  - 数値列: {len(df.select_dtypes(include=['number']).columns)}個\n")
                f.write(f"  - 文字列列: {len(df.select_dtypes(include=['object']).columns)}個\n")
                f.write(f"  - 出力ファイル: 選挙区_{sheet_name}_最終版.csv\n")
                f.write("\n")
    
    print(f"📝 サマリーレポートを保存しました: {summary_file}")

def main():
    """
    メイン関数
    """
    print("=== 埼玉投票情報分析プログラム（選挙区版） ===")
    print("📂 出力ディレクトリ:")
    print("   - tmp_info/: クリーンアップ前のデータ")
    print("   - output_info/: 最終的な処理済みデータ")
    print("")
    
    # 全シートのデータを読み込む
    all_sheet_data = load_excel_sheets()
    
    if all_sheet_data is None:
        print("データの読み込みに失敗しました。")
        return
    
    # 処理済みデータを保存するための辞書
    all_processed_data = {}
    
    # 各シートを処理してCSVに保存
    for sheet_name, sheet_data in all_sheet_data.items():
        print(f"\n{'='*50}")
        print(f"処理中のシート: {sheet_name}")
        print(f"{'='*50}")
        
        # データをクリーンアップしてCSVに保存
        cleaned_data = clean_and_save_sheet_data(sheet_data, sheet_name)
        all_processed_data[sheet_name] = cleaned_data
        
        # 基本的な分析を実行
        analyze_voting_info_data(cleaned_data)
    
    # 全体のサマリーレポートを作成
    create_summary_report(all_processed_data)
    
    print(f"\n{'='*60}")
    print("🎉 選挙区投票情報データの処理が完了しました！")
    print("📁 出力ファイルの確認:")
    print("   - tmp_info/: 元データのバックアップ")
    print("   - output_info/: 重複削除済みの最終データ")
    print("   - output_info/選挙区_投票情報処理サマリーレポート.txt: 処理結果の概要")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
