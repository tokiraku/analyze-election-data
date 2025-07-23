import pandas as pd
import os

def extract_complete_15_candidates_electoral():
    """
    15名全候補者の正確な抽出（選挙区データ専用）
    """
    print("=== 選挙区：15名候補者抽出中 ===")
    
    # 元のExcelファイルを読み込み
    df = pd.read_excel('埼玉投票結果_選挙区.xls', sheet_name='候補者別市区町村別得票調べ', engine='xlrd')
    
    # 15名の候補者と政党を正確に定義
    all_candidates = [
        '江原　くみ子', '津村　大作', '伊藤　岳', '矢倉　かつお', '武藤　かず子',
        '増山　ゆうか', '高井　たまき', '山田　信一', '桜井　ななえ', 'くまがい　裕人',
        'りゅうの　まゆみ', '古川　俊治', '大津　力', '斉藤　よしひで', '石濱　哲信'
    ]
    
    all_parties = [
        '国民民主党(新)', '日本改革党(新)', '日本共産党(現)', '公明党(現)', 'チームみらい(新)',
        '日本誠心会(新)', '社会民主党(新)', 'ＮＨＫ党(新)', 'れいわ新選組(新)', '立憲民主党(現)',
        '日本維新の会(新)', '自由民主党(現)', '参政党(新)', '無所属(新)', '日本保守党(新)'
    ]
    
    # データを格納するリスト
    vertical_data = []
    
    # 第1セクション: 最初の10名（列3-12）
    section1_municipalities = set()
    for i in range(14, 121):  # 修正された範囲：行14-120（松伏町を含む）
        if i < len(df):
            row = df.iloc[i]
            if str(row.iloc[0]) == '確定' and pd.notna(row.iloc[1]):
                municipality = str(row.iloc[1]).strip()
                
                if (municipality and 
                    municipality not in section1_municipalities and
                    any(suffix in municipality for suffix in ['市', '区', '町', '村']) and
                    all(exclude not in municipality for exclude in ['計', '合計', '県', '市区町村等'])):
                    
                    section1_municipalities.add(municipality)
                    
                    # 最初の10名の候補者データ（列3-12）
                    for j in range(10):
                        col_idx = 3 + j
                        if col_idx < len(row):
                            votes = row.iloc[col_idx]
                            if pd.notna(votes) and str(votes).strip() not in ['', 'nan', '0']:
                                try:
                                    vote_count = int(float(str(votes).strip()))
                                    if vote_count > 0:
                                        vertical_data.append({
                                            '市区町村名': municipality,
                                            '候補者名': all_candidates[j],
                                            '党派名等': all_parties[j],
                                            '得票数': vote_count
                                        })
                                except (ValueError, TypeError):
                                    pass
    
    # 第2セクション: 残りの5名（列3-7）
    section2_municipalities = set()
    for i in range(167, 275):  # 正確な範囲：行167-273
        if i < len(df):
            row = df.iloc[i]
            if str(row.iloc[0]) == '確定' and pd.notna(row.iloc[1]):
                municipality = str(row.iloc[1]).strip()
                
                if (municipality and 
                    municipality not in section2_municipalities and
                    any(suffix in municipality for suffix in ['市', '区', '町', '村']) and
                    all(exclude not in municipality for exclude in ['計', '合計', '県', '市区町村等'])):
                    
                    section2_municipalities.add(municipality)
                    
                    # 残りの5名の候補者データ（列3-7）
                    for j in range(5):
                        col_idx = 3 + j
                        candidate_idx = 10 + j
                        
                        if col_idx < len(row) and candidate_idx < len(all_candidates):
                            votes = row.iloc[col_idx]
                            if pd.notna(votes) and str(votes).strip() not in ['', 'nan', '0']:
                                try:
                                    vote_count = int(float(str(votes).strip()))
                                    if vote_count > 0:
                                        vertical_data.append({
                                            '市区町村名': municipality,
                                            '候補者名': all_candidates[candidate_idx],
                                            '党派名等': all_parties[candidate_idx],
                                            '得票数': vote_count
                                        })
                                except (ValueError, TypeError):
                                    pass
    
    # DataFrameに変換
    result_df = pd.DataFrame(vertical_data)
    
    # 重複削除
    result_df = result_df.drop_duplicates(subset=['市区町村名', '候補者名']).reset_index(drop=True)
    
    print(f"選挙区データ抽出完了: {len(result_df)}件、候補者数: {result_df['候補者名'].nunique()}名")
    
    return result_df

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
        '執行'
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
        '結果'
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
        'かりがね'
    ]
    
    for keyword in header_keywords:
        if keyword in text_str:
            return True
    
    return False

def load_excel_sheets():
    """
    埼玉投票結果_選挙区.xlsファイルの全シートを確認し、指定されたシートを読み込む関数
    """
    # ファイルパスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "埼玉投票結果_選挙区.xls")
    
    try:
        # まず、利用可能なシート名を確認
        print(f"ファイルを読み込み中: {file_path}")
        excel_file = pd.ExcelFile(file_path, engine='xlrd')
        print(f"利用可能なシート: {excel_file.sheet_names}")
        
        # 対象のシート名を定義
        target_sheets = ["候補者別市区町村別得票調べ", "市区町村別開票結果調べ"]
        sheet_data = {}
        
        for sheet_name in target_sheets:
            if sheet_name in excel_file.sheet_names:
                print(f"\nシート '{sheet_name}' を読み込み中...")
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                sheet_data[sheet_name] = df
                print(f"データの形状: {df.shape}")
                print(f"列名: {list(df.columns)}")
                print(f"データの先頭3行:")
                print(df.head(3))
            else:
                print(f"警告: シート '{sheet_name}' が見つかりません。")
        
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
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    tmp_filename = os.path.join(tmp_dir, f"{sheet_name}_クリーンアップ前.csv")
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
    
    print(f"✓ データクリーンアップが完了しました")
    
    return df

def transform_candidate_data_to_vertical(df):
    """
    候補者データを縦並び形式に変換する関数（全15名の候補者に対応）
    """
    print("--- 候補者データを縦並び形式に変換中（全15名対応） ---")
    
        # 第1セクション（最初の10名）の候補者データを抽出
    section1_candidates = []
    section1_parties = []
    
    # 候補者名行を探す（第1セクション）
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        if '候補者氏名' in str(row.iloc[0]):
            print(f"第1セクション候補者名行: {i}")
            # 列1-10から候補者名を抽出
            for col_idx in range(1, min(11, len(row))):
                val = str(row.iloc[col_idx]).strip()
                if pd.notna(row.iloc[col_idx]) and val and val != 'nan':
                    section1_candidates.append(val)
            
            # 次の行から党派名を取得
            if i + 1 < len(df):
                party_row = df.iloc[i + 1]
                for col_idx in range(1, min(11, len(party_row))):
                    val = str(party_row.iloc[col_idx]).strip()
                    if pd.notna(party_row.iloc[col_idx]) and val and val != 'nan':
                        section1_parties.append(val)
            break
    
    # 第2セクション（残りの5名）の候補者データを抽出
    section2_candidates = []
    section2_parties = []
    
    # 第2セクションの候補者名行を探す（行154-160周辺）
    for i in range(150, min(165, len(df))):
        if i < len(df):
            row = df.iloc[i]
            if '候補者氏名' in str(row.iloc[0]):
                print(f"第2セクション候補者名行: {i}")
                # 列1-5から候補者名を抽出
                for col_idx in range(1, min(6, len(row))):
                    val = str(row.iloc[col_idx]).strip()
                    if pd.notna(row.iloc[col_idx]) and val and val != 'nan':
                        section2_candidates.append(val)
                
                # 次の行から党派名を取得
                if i + 1 < len(df):
                    party_row = df.iloc[i + 1]
                    for col_idx in range(1, min(6, len(party_row))):
                        val = str(party_row.iloc[col_idx]).strip()
                        if pd.notna(party_row.iloc[col_idx]) and val and val != 'nan':
                            section2_parties.append(val)
                break
    
    # 全候補者リストを結合
    all_candidates = section1_candidates + section2_candidates
    all_parties = section1_parties + section2_parties
    
    print(f"第1セクション候補者({len(section1_candidates)}名): {section1_candidates}")
    print(f"第2セクション候補者({len(section2_candidates)}名): {section2_candidates}")
    print(f"全候補者({len(all_candidates)}名): {all_candidates}")
    print(f"全党派名: {all_parties}")
    
    if not all_candidates:
        print("⚠️ 候補者名が抽出できませんでした")
        return df
    
    # データ行の抽出（第1セクションと第2セクション）
    section1_data_rows = []
    section2_data_rows = []
    
    # 第1セクションのデータ行（行7-55頃）
    for idx in range(7, 60):
        if idx < len(df):
            row = df.iloc[idx]
            municipality_col = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if (municipality_col and 
                municipality_col != '' and 
                municipality_col not in ['nan', 'NaN', '市区町村名'] and
                not any(keyword in municipality_col for keyword in ['選挙', '候補者', '政党', '得票', '調べ', '結果', '計']) and
                '確定' in str(row.iloc[0])):
                section1_data_rows.append(row)
    
    # 第2セクションのデータ行（行168以降）
    for idx in range(168, min(220, len(df))):
        row = df.iloc[idx]
        municipality_col = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        if (municipality_col and 
            municipality_col != '' and 
            municipality_col not in ['nan', 'NaN', '市区町村名'] and
            not any(keyword in municipality_col for keyword in ['選挙', '候補者', '政党', '得票', '調べ', '結果', '計']) and
            '確定' in str(row.iloc[0])):
            section2_data_rows.append(row)
    
    print(f"第1セクションデータ行数: {len(section1_data_rows)}")
    print(f"第2セクションデータ行数: {len(section2_data_rows)}")
    
    if not section1_data_rows and not section2_data_rows:
        print("⚠️ データ行が見つかりません")
        return df
    
    # 縦並び形式に変換
    vertical_data = []
    
    # 第1セクションのデータを処理
    for row in section1_data_rows:
        municipality = str(row.iloc[1]).strip()
        
        # 第1セクションの10名の候補者データを処理（列3-12）
        for i, (candidate, party) in enumerate(zip(section1_candidates, section1_parties)):
            vote_col_idx = 3 + i
            if vote_col_idx < len(row):
                votes = row.iloc[vote_col_idx]
                if pd.notna(votes) and str(votes).strip() != '' and str(votes).strip() != 'nan':
                    try:
                        vote_count = int(float(str(votes).strip()))
                        vertical_data.append({
                            '市区町村名': municipality,
                            '候補者名': candidate,
                            '党派名等': party,
                            '得票数': vote_count
                        })
                    except (ValueError, TypeError):
                        vertical_data.append({
                            '市区町村名': municipality,
                            '候補者名': candidate,
                            '党派名等': party,
                            '得票数': str(votes).strip()
                        })
    
    # 第2セクションのデータを処理
    for row in section2_data_rows:
        municipality = str(row.iloc[1]).strip()
        
        # 第2セクションの5名の候補者データを処理（列2-6: 届出番号11-15）
        for i, (candidate, party) in enumerate(zip(section2_candidates, section2_parties)):
            vote_col_idx = 2 + i  # 第2セクションは列2から開始
            if vote_col_idx < len(row):
                votes = row.iloc[vote_col_idx]
                if pd.notna(votes) and str(votes).strip() != '' and str(votes).strip() != 'nan':
                    try:
                        vote_count = int(float(str(votes).strip()))
                        vertical_data.append({
                            '市区町村名': municipality,
                            '候補者名': candidate,
                            '党派名等': party,
                            '得票数': vote_count
                        })
                    except (ValueError, TypeError):
                        vertical_data.append({
                            '市区町村名': municipality,
                            '候補者名': candidate,
                            '党派名等': party,
                            '得票数': str(votes).strip()
                        })
    
    # DataFrameに変換
    vertical_df = pd.DataFrame(vertical_data)
    
    if not vertical_df.empty:
        print(f"✅ 縦並び変換完了: {len(vertical_df)}件のデータ")
        print(f"対象候補者数: {vertical_df['候補者名'].nunique()}人")
        print(f"対象市区町村数: {vertical_df['市区町村名'].nunique()}箇所")
        print(f"全候補者リスト: {sorted(vertical_df['候補者名'].unique())}")
    
    return vertical_df

def transform_election_results_to_vertical(df):
    """
    選挙結果データを縦並び形式に変換する関数
    """
    print("--- 選挙結果データを縦並び形式に変換中 ---")
    
    # ヘッダー行を特定
    header_row = None
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val) for val in row.values if pd.notna(val)])
        if '（Ａ）' in row_str and '（Ｂ）' in row_str:
            header_row = idx
            break
    
    if header_row is None:
        print("⚠️ ヘッダー行が見つかりません")
        return df
    
    # ヘッダーを取得し、意味のある名前にマッピング
    headers = df.iloc[header_row].values
    
    # 選挙結果データの列名マッピング辞書
    header_mapping = {
        '（Ａ）': '有効投票総数',
        '（Ｂ）': '按分票数',
        '（Ａ＋Ｂ）（Ｃ）': '有効投票数_計',
        '（Ｄ）': '無効投票数',
        '（Ｄ÷Ｅ）％': '無効投票率_パーセント',
        '（Ｃ＋Ｄ）（Ｅ）': '投票総数',
        '（Ｆ）': '持帰り票数',
        '（Ｇ）': '不受理票数',
        '（Ｈ）': 'その他',
        '（Ｅ＋Ｆ＋Ｇ＋Ｈ）': '投票者総数',
        '時': '確定時刻_時',
        '分': '確定時刻_分'
    }
    
    clean_headers = []
    for h in headers:
        if pd.notna(h) and str(h).strip():
            header_str = str(h).strip()
            # マッピング辞書から対応する意味のある名前を取得
            meaningful_name = header_mapping.get(header_str, header_str)
            clean_headers.append(meaningful_name)
        else:
            clean_headers.append('')
    
    print(f"変換後のヘッダー: {clean_headers[:8]}...")
    
    # データ行のみを抽出
    data_rows = []
    for idx, row in df.iterrows():
        if idx != header_row and pd.notna(row.iloc[0]) and str(row.iloc[0]).strip():
            municipality = row.iloc[0]
            if municipality not in ['', '（Ａ）', '（Ｂ）']:
                data_dict = {'市区町村名': municipality}
                for i, header in enumerate(clean_headers[1:], 1):
                    if i < len(row) and header:
                        value = row.iloc[i]
                        data_dict[header] = value
                data_rows.append(data_dict)
    
    if not data_rows:
        print("⚠️ データ行が見つかりません")
        return df
    
    # DataFrameに変換
    vertical_df = pd.DataFrame(data_rows)
    
    if not vertical_df.empty:
        print(f"✅ 縦並び変換完了: {len(vertical_df)}件のデータ")
        print(f"対象市区町村数: {vertical_df['市区町村名'].nunique()}箇所")
        
        # 列名を表示
        print(f"出力列名: {list(vertical_df.columns)}")
    
    return vertical_df

def analyze_voting_data(df):
    """
    投票データの基本的な分析を行う関数
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
    print("📊 処理結果サマリーレポート")
    print(f"{'='*60}")
    
    output_dir = "output"
    summary_file = os.path.join(output_dir, "処理サマリーレポート.txt")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("埼玉投票結果分析 - 処理サマリーレポート\n")
        f.write(f"処理日時: {pd.Timestamp.now()}\n")
        f.write("="*60 + "\n\n")
        
        for sheet_name, df in all_processed_data.items():
            if df is not None:
                f.write(f"シート: {sheet_name}\n")
                f.write(f"  - 最終行数: {len(df)}\n")
                f.write(f"  - 列数: {len(df.columns)}\n")
                f.write(f"  - 数値列: {len(df.select_dtypes(include=['number']).columns)}個\n")
                f.write(f"  - 文字列列: {len(df.select_dtypes(include=['object']).columns)}個\n")
                f.write(f"  - 出力ファイル: {sheet_name}_縦並び版.csv\n")
                f.write("\n")
    
    print(f"📝 サマリーレポートを保存しました: {summary_file}")

def main():
    """
    メイン関数
    """
    print("=== 埼玉投票結果分析プログラム ===")
    print("📂 出力ディレクトリ:")
    print("   - tmp/: クリーンアップ前のデータ")
    print("   - output/: 最終的な処理済みデータ")
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
        
        # データをクリーンアップ
        cleaned_data = clean_and_save_sheet_data(sheet_data, sheet_name)
        
        # outputディレクトリを作成
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 縦並び変換を実行して保存
        if sheet_name == "候補者別市区町村別得票調べ":
            # 新しい15名完全抽出関数を使用
            vertical_data = extract_complete_15_candidates_electoral()
            if not vertical_data.empty:
                vertical_filename = os.path.join(output_dir, f"{sheet_name}_縦並び版.csv")
                vertical_data.to_csv(vertical_filename, index=False, encoding='utf-8-sig')
                print(f"✅ 縦並び版CSVファイルを保存しました: {vertical_filename}")
                print(f"縦並び版データの先頭5行:")
                print(vertical_data.head())
                
                # 縦並び版のデータを保存
                all_processed_data[sheet_name] = vertical_data
                # 分析を実行
                analyze_voting_data(vertical_data)
        
        elif sheet_name == "市区町村別開票結果調べ":
            vertical_data = transform_election_results_to_vertical(cleaned_data)
            if not vertical_data.empty:
                vertical_filename = os.path.join(output_dir, f"{sheet_name}_縦並び版.csv")
                vertical_data.to_csv(vertical_filename, index=False, encoding='utf-8-sig')
                print(f"✅ 縦並び版CSVファイルを保存しました: {vertical_filename}")
                print(f"縦並び版データの先頭5行:")
                print(vertical_data.head())
                
                # 縦並び版のデータを保存
                all_processed_data[sheet_name] = vertical_data
                # 分析を実行
                analyze_voting_data(vertical_data)
        
        else:
            # 他のシートはそのまま保存
            all_processed_data[sheet_name] = cleaned_data
    
    # 全体のサマリーレポートを作成
    create_summary_report(all_processed_data)
    
    print(f"\n{'='*60}")
    print("🎉 選挙区データの処理が完了しました！")
    print("📁 出力ファイルの確認:")
    print("   - tmp/: 元データのバックアップ")
    print("   - output/: 縦並び版の最終データ")
    print("   - output/*_縦並び版.csv: 各シートの縦並び版データ")
    print("   - output/処理サマリーレポート.txt: 処理結果の概要")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()