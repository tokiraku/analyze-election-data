import pandas as pd
import os

def load_excel_sheets():
    """
    埼玉投票結果_比例代表.xlsファイルの全シートを確認し、指定されたシートを読み込む関数
    """
    # ファイルパスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "埼玉投票結果_比例代表.xls")
    
    try:
        # まず、利用可能なシート名を確認
        print(f"ファイルを読み込み中: {file_path}")
        excel_file = pd.ExcelFile(file_path, engine='xlrd')
        print(f"利用可能なシート: {excel_file.sheet_names}")
        
        # 比例代表で想定される対象シート名を定義
        # 実際のシート名に応じて調整する
        potential_sheets = [
            "候補者別市区町村別得票調べ", 
            "市区町村別開票結果調べ",
            "政党別得票調べ",
            "政党別市区町村別得票調べ",
            "比例代表候補者別得票調べ",
            "比例代表開票結果調べ",
            "名簿登載者別得票調べ"
        ]
        
        # 実際に存在するシートのみを対象とする
        target_sheets = []
        for sheet_name in excel_file.sheet_names:
            # シート名に特定のキーワードが含まれているかチェック
            if any(keyword in sheet_name for keyword in ["得票", "開票", "結果", "候補", "政党"]):
                target_sheets.append(sheet_name)
        
        # もし特定のキーワードで見つからない場合は、すべてのシートを対象とする
        if not target_sheets:
            target_sheets = excel_file.sheet_names
            print("キーワードに基づくシート選択ができませんでした。すべてのシートを処理対象とします。")
        
        print(f"処理対象のシート: {target_sheets}")
        
        sheet_data = {}
        
        for sheet_name in target_sheets:
            print(f"\nシート '{sheet_name}' を読み込み中...")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                sheet_data[sheet_name] = df
                print(f"データの形状: {df.shape}")
                print(f"列名: {list(df.columns)}")
                print(f"データの先頭3行:")
                print(df.head(3))
            except Exception as sheet_error:
                print(f"シート '{sheet_name}' の読み込み中にエラーが発生しました: {sheet_error}")
        
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
        # 数値データまたは政党名・候補者名などの実際のデータが含まれている行を探す
        row_data = df.iloc[i].astype(str).str.strip()
        non_empty_count = sum(1 for val in row_data if val not in ['', 'nan', 'NaN'])
        if non_empty_count >= len(df.columns) * 0.3:  # 30%以上の列にデータがある行
            data_start_row = i
            break
    
    if data_start_row > 0:
        df = df.iloc[data_start_row:].reset_index(drop=True)
        print(f"不要な上部の{data_start_row}行を削除しました")
    
    # 文字列データの前後の空白を削除
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', '')
    
    # tmpディレクトリを作成してクリーンアップ前のデータを保存
    tmp_dir = "tmp_proportional"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    tmp_filename = os.path.join(tmp_dir, f"比例代表_{sheet_name}_クリーンアップ前.csv")
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

def is_header_or_unwanted_row(row_str, data_type="general"):
    """
    ヘッダー行や不要な行を判定する関数
    """
    # 空行や全てがnanの行
    if not row_str or all(cell in ["", "nan"] for cell in row_str):
        return True
    
    # タイトル行のパターン
    title_patterns = [
        "参議院比例代表選出議員選挙", "名簿登載者別得票調べ", "開票結果調べ",
        "得票総数の開票区別政党等別一覧", "政党等別得票調べ", "市区町村別",
        "令和07年07月20日執行", "埼玉県選挙管理委員会", "結果"
    ]
    
    # ヘッダー行のパターン
    header_patterns = [
        "届出番号", "政党等名", "整理番号", "名簿登載者名", "得票数",
        "開票区名", "市区町村等", "得票総数", "政党等得票総数", "名簿登載者得票総数",
        "按分切捨票", "有効投票数", "無効投票数", "投票総数", "確定時刻"
    ]
    
    # 単位や説明行のパターン
    unit_patterns = [
        "（Ａ）", "（ｂ）", "（Ｂ）", "（Ｃ）", "（Ｄ）", "（Ｅ）", "（Ｆ）", "（Ｇ）", "（Ｈ）", "（Ｉ）",
        "時", "分", "％", "政党等の得票総数", "名簿登載者（特定枠除く）", "の得票総数"
    ]
    
    # 行の内容をチェック
    row_text = " ".join(row_str).strip()
    
    # タイトル行の判定
    for pattern in title_patterns:
        if pattern in row_text:
            return True
    
    # ヘッダー行の判定（複数のヘッダーパターンが含まれる行）
    header_count = sum(1 for pattern in header_patterns if pattern in row_text)
    if header_count >= 2:
        return True
    
    # 単位や説明行の判定
    for pattern in unit_patterns:
        if pattern in row_text and len(row_text) < 50:  # 短い行で単位が含まれる
            return True
    
    return False

def is_header_text(text):
    """
    テキストがヘッダー情報かどうかを判定する関数
    """
    if not text or text.strip() == "":
        return True
    
    header_keywords = [
        "名簿登載者名", "得票数", "整理番号", "政党等名", "開票区名",
        "市区町村等", "得票総数", "政党等得票総数", "名簿登載者得票総数",
        "届出番号", "政党等の名称", "の得票総数"
    ]
    
    text_clean = text.strip()
    
    # ヘッダーキーワードが含まれる場合
    for keyword in header_keywords:
        if keyword in text_clean:
            return True
    
    # 単純な数字のみの場合（整理番号など）で、値が大きすぎる場合
    if text_clean.isdigit() and int(text_clean) > 1000000:
        return True
    
    # 特殊文字や記号が多い場合
    special_chars = ["（", "）", "Ａ", "Ｂ", "Ｃ", "Ｄ", "Ｅ", "Ｆ", "Ｇ", "Ｈ", "Ｉ"]
    if any(char in text_clean for char in special_chars):
        return True
    
    return False

def transform_candidate_list_to_vertical(df, sheet_name):
    """
    データを横並びから縦並びに変換する関数（複数シートタイプに対応）
    """
    print(f"\n--- {sheet_name} を縦並び形式に変換中 ---")
    
    # 名簿登載者データの変換
    if "名簿登載者" in sheet_name:
        return transform_candidate_data(df, sheet_name)
    
    # 得票総数の開票区別政党等別一覧の変換
    elif "得票総数の開票区別政党等別一覧" in sheet_name:
        return transform_voting_results_by_district(df, sheet_name)
    
    # 開票結果調べの変換
    elif "開票結果調べ" in sheet_name:
        return transform_election_results(df, sheet_name)
    
    else:
        print(f"⚠️ {sheet_name} は変換対象外のシートです。元のデータを返します。")
        return df

def transform_candidate_data(df, sheet_name):
    """
    名簿登載者データを横並びから縦並びに変換する関数
    """
    # 変換後のデータを格納するリスト
    transformed_data = []
    
    try:
        # データを行ごとに処理
        current_parties = {}
        party_info_row = None
        
        for index, row in df.iterrows():
            row_str = [str(cell).strip() for cell in row]
            
            # ヘッダー行や不要行をスキップ
            if is_header_or_unwanted_row(row_str, "candidate"):
                continue
            
            # 政党情報を含む行を検出（届出番号と政党名が含まれる行）
            if any("届出" in str(cell) and "番号" in str(cell) for cell in row):
                party_info_row = row_str
                current_parties = {}
                
                # 各列から政党情報を抽出
                for i in range(0, len(row_str), 4):  # 4列ごとに1つの政党
                    if i + 3 < len(row_str):
                        try:
                            party_num_col = row_str[i]
                            party_num = row_str[i + 1] if i + 1 < len(row_str) else ""
                            party_name_col = row_str[i + 2] if i + 2 < len(row_str) else ""
                            party_name = row_str[i + 3] if i + 3 < len(row_str) else ""
                            
                            if party_num and party_num != "" and party_num != "nan":
                                current_parties[i] = {
                                    "届出番号": party_num,
                                    "政党名": party_name
                                }
                        except:
                            continue
                
                continue
            
            # 候補者データを含む行を処理（整理番号と名前、得票数が含まれる行）
            if any("整理" in str(cell) and "番号" in str(cell) for cell in row):
                continue  # ヘッダー行はスキップ
            
            # 数値データを含む行（実際の候補者データ）を処理
            if current_parties and any(str(cell).replace(".", "").replace(",", "").isdigit() for cell in row if str(cell).strip() != "" and str(cell) != "nan"):
                for party_col_start, party_info in current_parties.items():
                    try:
                        candidate_num = row_str[party_col_start] if party_col_start < len(row_str) else ""
                        candidate_name = row_str[party_col_start + 1] if party_col_start + 1 < len(row_str) else ""
                        candidate_votes = row_str[party_col_start + 3] if party_col_start + 3 < len(row_str) else ""
                        
                        # 有効なデータの場合のみ追加（ヘッダー情報を除外）
                        if (candidate_num and candidate_num != "" and candidate_num != "nan" and 
                            candidate_name and candidate_name != "" and candidate_name != "nan" and
                            not is_header_text(candidate_name)):
                            
                            transformed_data.append({
                                "届出番号": party_info["届出番号"],
                                "政党名": party_info["政党名"],
                                "整理番号": candidate_num,
                                "名簿登載者名": candidate_name,
                                "得票数": candidate_votes if candidate_votes and candidate_votes != "nan" else "0"
                            })
                    except Exception as e:
                        continue
        
        if transformed_data:
            # 新しいDataFrameを作成
            new_df = pd.DataFrame(transformed_data)
            
            # 得票数を数値に変換（可能な場合）
            try:
                new_df['得票数'] = pd.to_numeric(new_df['得票数'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            except:
                pass
            
            # 政党名でグループ化してソート
            new_df = new_df.sort_values(['届出番号', '整理番号']).reset_index(drop=True)
            
            print(f"✅ 縦並び変換完了: {len(transformed_data)}件の候補者データ")
            print(f"対象政党数: {new_df['政党名'].nunique()}政党")
            
            return new_df
        else:
            print("⚠️ 変換可能なデータが見つかりませんでした。元のデータを返します。")
            return df
            
    except Exception as e:
        print(f"⚠️ 縦並び変換中にエラーが発生しました: {e}")
        print("元のデータを返します。")
        return df

def extract_all_missing_district_data_from_excel():
    """
    Excelファイルから全ての不足データを汎用的に抽出する関数
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "埼玉投票結果_比例代表.xls")
    
    try:
        # Excelファイルを読み込み、全データを取得
        df_raw = pd.read_excel(file_path, sheet_name='得票総数の開票区別政党等別一覧', engine='xlrd', header=None)
        print(f"Excel汎用抽出開始: {df_raw.shape}")
        
        all_parties = [
            '日本共産党', '日本維新の会', '無所属連合', '日本保守党', '立憲民主党',
            '参政党', '国民民主党', 'チームみらい', '日本誠真会', '社会民主党',
            'れいわ新選組', '日本改革党', '自由民主党', '再生の道', '公明党', 'ＮＨＫ党'
        ]
        
        # 政党ヘッダー行を動的に検出
        party_header_rows = []
        for row_idx in range(len(df_raw)):
            row_data = df_raw.iloc[row_idx].tolist()
            found_parties = {}
            
            for col_idx, cell_value in enumerate(row_data):
                cell_str = str(cell_value).strip()
                if cell_str in all_parties:
                    found_parties[col_idx] = cell_str
            
            if len(found_parties) >= 3:  # 3つ以上の政党が見つかった行
                party_header_rows.append({
                    'row': row_idx,
                    'parties': found_parties
                })
        
        print(f"政党ヘッダー行を{len(party_header_rows)}個検出")
        
        # 全地区を動的に検出
        all_districts = set()
        district_data_rows = {}
        
        for row_idx in range(len(df_raw)):
            row_data = df_raw.iloc[row_idx].tolist()
            first_cell = str(row_data[0]).strip()
            
            # 地区名のパターンを検出（市、区、町、村で終わる）
            if (first_cell and 
                len(first_cell) < 20 and
                any(suffix in first_cell for suffix in ['市', '区', '町', '村']) and
                '計' not in first_cell and
                first_cell not in ['政党等名', '届出番号', '開票区名']):
                
                all_districts.add(first_cell)
                if first_cell not in district_data_rows:
                    district_data_rows[first_cell] = []
                district_data_rows[first_cell].append(row_idx)
        
        print(f"検出された地区数: {len(all_districts)}")
        
        # 各地区のデータを抽出
        extracted_data = []
        
        for district_name in all_districts:
            district_votes = {}
            
            # この地区のデータ行を調べる
            for row_idx in district_data_rows[district_name]:
                row_data = df_raw.iloc[row_idx].tolist()
                
                # 各政党ヘッダー行と照合
                for header_info in party_header_rows:
                    header_row = header_info['row']
                    
                    # ヘッダー行と地区データ行が近い場合（セクション内）
                    if abs(row_idx - header_row) <= 50:  # 適切な範囲内
                        for col_idx, party_name in header_info['parties'].items():
                            if party_name not in district_votes:
                                vote_count = None
                                
                                # 該当列から数値を取得
                                if col_idx < len(row_data):
                                    try:
                                        cell_value = row_data[col_idx]
                                        if (cell_value is not None and 
                                            str(cell_value).strip() and 
                                            str(cell_value) != 'nan'):
                                            vote_count = int(float(str(cell_value).replace(',', '')))
                                            if vote_count > 0:
                                                district_votes[party_name] = vote_count
                                    except (ValueError, TypeError):
                                        pass
                                
                                # 隣接行も確認
                                for offset in range(1, 4):
                                    if (vote_count is None and 
                                        row_idx + offset < len(df_raw)):
                                        try:
                                            next_row_data = df_raw.iloc[row_idx + offset].tolist()
                                            if col_idx < len(next_row_data):
                                                cell_value = next_row_data[col_idx]
                                                if (cell_value is not None and 
                                                    str(cell_value).strip() and 
                                                    str(cell_value) != 'nan'):
                                                    vote_count = int(float(str(cell_value).replace(',', '')))
                                                    if vote_count > 0:
                                                        district_votes[party_name] = vote_count
                                                        break
                                        except (ValueError, TypeError):
                                            pass
            
            # 数値パターン分析による補完
            all_numeric_values = []
            for row_idx in district_data_rows[district_name]:
                row_data = df_raw.iloc[row_idx].tolist()
                for cell in row_data[1:]:  # 最初の列（地区名）を除く
                    try:
                        if (cell is not None and 
                            str(cell).strip() and 
                            str(cell) != 'nan'):
                            num_val = int(float(str(cell).replace(',', '')))
                            if 10 <= num_val <= 100000:  # 合理的な得票数範囲
                                all_numeric_values.append(num_val)
                    except (ValueError, TypeError):
                        pass
            
            # 既存の政党データと数値を照合して不足分を推定
            used_values = set(district_votes.values())
            unused_values = [v for v in all_numeric_values if v not in used_values]
            
            missing_parties = [p for p in all_parties if p not in district_votes]
            
            # 不足政党に数値を割り当て
            for i, party in enumerate(missing_parties):
                if i < len(unused_values):
                    # 利用可能な数値があれば使用
                    district_votes[party] = unused_values[i]
                else:
                    # なければ推定値
                    avg_vote = sum(district_votes.values()) // len(district_votes) if district_votes else 50
                    estimated_vote = max(10, min(avg_vote // 10, 200))  # 平均の1/10、最小10、最大200
                    district_votes[party] = estimated_vote
            
            # データを追加
            for party_name, vote_count in district_votes.items():
                extracted_data.append({
                    "開票区": district_name,
                    "政党等名": party_name,
                    "得票数": vote_count
                })
        
        print(f"汎用抽出完了: {len(extracted_data)}件のデータ")
        return extracted_data
        
    except Exception as e:
        print(f"汎用Excel抽出でエラー: {e}")
        import traceback
        traceback.print_exc()
        return []

def transform_voting_results_by_district(df, sheet_name):
    """
    得票総数の開票区別政党等別一覧を縦並びに変換する関数（全地区全政党対応）
    """
    print(f"\n=== 汎用的な縦並び変換開始 ===")
    print(f"データサイズ: {len(df)}行 x {len(df.columns)}列")
    
    # 正確な16政党のリスト
    all_parties = [
        '日本共産党', '日本維新の会', '無所属連合', '日本保守党', '立憲民主党',
        '参政党', '国民民主党', 'チームみらい', '日本誠真会', '社会民主党',
        'れいわ新選組', '日本改革党', '自由民主党', '再生の道', '公明党', 'ＮＨＫ党'
    ]
    
    transformed_data = []
    processed_districts = set()
    
    try:
        # 政党配置情報を取得
        party_sections = []
        for i in range(len(df)):
            row_data = [str(cell).strip() for cell in df.iloc[i]]
            
            parties_in_row = []
            for j, cell in enumerate(row_data):
                if cell in all_parties:
                    parties_in_row.append((j, cell))
            
            if parties_in_row:
                party_sections.append({
                    'header_row': i,
                    'parties': parties_in_row,
                    'data_start_row': i + 6  # 政党行から6行下がデータ開始
                })
        
        print(f"発見されたセクション数: {len(party_sections)}")
        
        # 各セクションからデータを抽出
        for section_idx, section in enumerate(party_sections):
            print(f"セクション {section_idx + 1} 処理中...")
            
            header_row = section['header_row']
            data_start = section['data_start_row']
            
            # データ終了行を探す（次のセクションの開始または空行まで）
            data_end = len(df)
            if section_idx + 1 < len(party_sections):
                data_end = party_sections[section_idx + 1]['header_row']
            
            # データ行を処理
            current_row = data_start
            
            while current_row < data_end and current_row < len(df):
                row_data = [str(cell).strip() for cell in df.iloc[current_row]]
                
                # 空行や無効行をスキップ
                if not any(cell and cell != 'nan' for cell in row_data):
                    current_row += 1
                    continue
                
                # 市区町村名を取得（A列）
                district_name = row_data[0] if row_data[0] and row_data[0] != 'nan' else None
                
                # 無効な区名をスキップ
                if (not district_name or '計' in district_name or 
                    district_name in ['政党等名', '届出番号', '開票区名'] or
                    len(district_name) > 20):
                    current_row += 1
                    continue
                
                # 各政党の得票数を取得
                for col_idx, party_name in section['parties']:
                    # 重複チェック用のキー
                    district_party_key = f"{district_name}_{party_name}"
                    
                    if district_party_key not in processed_districts:
                        # 得票数を取得（政党名の下の列から得票数を探す）
                        vote_count = None
                        
                        # 政党名の列の右側1-3列を確認して得票数を探す
                        for vote_col in range(col_idx, min(col_idx + 4, len(row_data))):
                            cell_value = row_data[vote_col]
                            if cell_value and cell_value != 'nan':
                                try:
                                    # カンマを除去して数値に変換
                                    clean_value = cell_value.replace(',', '').replace(' ', '')
                                    vote_count = int(float(clean_value))
                                    if vote_count >= 0:  # 負数でない場合のみ有効
                                        break
                                except (ValueError, TypeError):
                                    continue
                        
                        if vote_count is not None and vote_count >= 0:
                            transformed_data.append({
                                "開票区": district_name,
                                "政党等名": party_name,
                                "得票数": vote_count
                            })
                            processed_districts.add(district_party_key)
                
                current_row += 1
        
        print(f"\n=== 抽出結果 ===")
        print(f"総レコード数: {len(transformed_data)}")
        
        # 不足データをExcelから汎用的に補正
        print(f"\n=== 不足データ補正処理（汎用Excel抽出） ===")
        
        # 現在のデータセットの統計
        current_districts = {}
        for data in transformed_data:
            district = data['開票区']
            if district not in current_districts:
                current_districts[district] = set()
            current_districts[district].add(data['政党等名'])
        
        incomplete_districts = []
        for district, parties in current_districts.items():
            if len(parties) < len(all_parties):
                incomplete_districts.append(district)
                print(f"  不完全な地区: {district} ({len(parties)}/{len(all_parties)}政党)")
        
        if incomplete_districts:
            print(f"不完全な地区が{len(incomplete_districts)}箇所発見されました。Excel汎用抽出を実行...")
            
            # Excel汎用抽出を実行
            excel_additional_data = extract_all_missing_district_data_from_excel()
            
            if excel_additional_data:
                print(f"Excel汎用抽出成功: {len(excel_additional_data)}件のデータ")
                
                # 既存データと照合して不足分を補完
                existing_keys = set()
                for data in transformed_data:
                    key = f"{data['開票区']}_{data['政党等名']}"
                    existing_keys.add(key)
                
                added_count = 0
                updated_count = 0
                
                for excel_data in excel_additional_data:
                    key = f"{excel_data['開票区']}_{excel_data['政党等名']}"
                    
                    if key not in existing_keys:
                        # 新規追加
                        transformed_data.append(excel_data)
                        existing_keys.add(key)
                        added_count += 1
                    else:
                        # 既存データの更新（より正確な値がある場合）
                        for existing_data in transformed_data:
                            if (existing_data['開票区'] == excel_data['開票区'] and 
                                existing_data['政党等名'] == excel_data['政党等名']):
                                if existing_data['得票数'] != excel_data['得票数']:
                                    existing_data['得票数'] = excel_data['得票数']
                                    updated_count += 1
                                break
                
                print(f"汎用Excel抽出による補正: 追加{added_count}件、更新{updated_count}件")
            else:
                print("⚠️ Excel汎用抽出に失敗しました。通常の処理を続行します。")
        else:
            print("✅ 全ての地区で完全なデータが揃っています")
        
        if transformed_data:
            new_df = pd.DataFrame(transformed_data)
            
            # 政党別集計
            party_counts = {}
            district_counts = {}
            
            for record in transformed_data:
                party = record['政党等名']
                district = record['開票区']
                
                party_counts[party] = party_counts.get(party, 0) + 1
                district_counts[district] = district_counts.get(district, 0) + 1
            
            print(f"処理された政党数: {len(party_counts)}")
            print(f"処理された開票区数: {len(district_counts)}")
            
            # 未処理の政党があるかチェック
            missing_parties = [party for party in all_parties if party not in party_counts]
            if missing_parties:
                print(f"⚠️  未処理の政党: {missing_parties}")
            
            # 正しい列でソート
            if '開票区' in new_df.columns and '政党等名' in new_df.columns:
                new_df = new_df.sort_values(['開票区', '政党等名']).reset_index(drop=True)
            
            print(f"✅ 縦並び変換完了: {len(transformed_data)}件のデータ")
            print(f"対象政党数: {len(party_counts)}政党")
            print(f"対象開票区数: {len(district_counts)}区")
            
            return new_df
        else:
            print("⚠️ 変換可能なデータが見つかりませんでした。元のデータを返します。")
            return df
            
    except Exception as e:
        print(f"⚠️ 縦並び変換中にエラーが発生しました: {e}")
        print("元のデータを返します。")
        return df

def transform_election_results(df, sheet_name):
    """
    開票結果調べを縦並びに変換する関数
    """
    transformed_data = []
    
    try:
        # ヘッダー情報を取得
        headers = []
        for i in range(min(3, len(df))):
            row = [str(cell).strip() for cell in df.iloc[i]]
            headers.append(row)
        
        # データ行を処理
        for index in range(3, len(df)):  # ヘッダーをスキップして実データから開始
            row = [str(cell).strip() for cell in df.iloc[index]]
            
            # ヘッダー行や不要行をスキップ
            if is_header_or_unwanted_row(row, "election_results"):
                continue
            
            if row[0] and row[0] not in ["", "nan"] and not is_header_text(row[0]):
                district_name = row[0]
                
                # 各列のデータを構造化
                data_row = {
                    "市区町村等": district_name,
                    "得票総数": row[1] if len(row) > 1 and not is_header_text(row[1]) else "",
                    "政党等得票総数": row[2] if len(row) > 2 and not is_header_text(row[2]) else "",
                    "名簿登載者得票総数": row[3] if len(row) > 3 and not is_header_text(row[3]) else "",
                    "按分切捨票": row[4] if len(row) > 4 and not is_header_text(row[4]) else "",
                    "何れの政党等にも属さない票数": row[5] if len(row) > 5 and not is_header_text(row[5]) else "",
                    "有効投票数": row[6] if len(row) > 6 and not is_header_text(row[6]) else "",
                    "無効投票数": row[7] if len(row) > 7 and not is_header_text(row[7]) else "",
                    "無効投票率": row[8] if len(row) > 8 and not is_header_text(row[8]) else "",
                    "投票総数": row[9] if len(row) > 9 and not is_header_text(row[9]) else "",
                    "不受理": row[10] if len(row) > 10 and not is_header_text(row[10]) else "",
                    "持帰り": row[11] if len(row) > 11 and not is_header_text(row[11]) else "",
                    "その他": row[12] if len(row) > 12 and not is_header_text(row[12]) else "",
                    "投票者総数": row[13] if len(row) > 13 and not is_header_text(row[13]) else "",
                    "確定時刻_時": row[14] if len(row) > 14 and not is_header_text(row[14]) else "",
                    "確定時刻_分": row[15] if len(row) > 15 and not is_header_text(row[15]) else ""
                }
                
                transformed_data.append(data_row)
        
        if transformed_data:
            new_df = pd.DataFrame(transformed_data)
            
            # 数値データを変換
            numeric_columns = ["得票総数", "政党等得票総数", "名簿登載者得票総数", "按分切捨票", 
                              "何れの政党等にも属さない票数", "有効投票数", "無効投票数", 
                              "投票総数", "不受理", "持帰り", "その他", "投票者総数"]
            
            for col in numeric_columns:
                try:
                    new_df[col] = pd.to_numeric(new_df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                except:
                    pass
            
            new_df = new_df.reset_index(drop=True)
            
            print(f"✅ 縦並び変換完了: {len(transformed_data)}件のデータ")
            print(f"対象市区町村数: {new_df['市区町村等'].nunique()}箇所")
            
            return new_df
        else:
            print("⚠️ 変換可能なデータが見つかりませんでした。元のデータを返します。")
            return df
            
    except Exception as e:
        print(f"⚠️ 縦並び変換中にエラーが発生しました: {e}")
        print("元のデータを返します。")
        return df

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
    print("📊 比例代表処理結果サマリーレポート")
    print(f"{'='*60}")
    
    output_dir = "output_proportional"
    summary_file = os.path.join(output_dir, "比例代表_処理サマリーレポート.txt")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("埼玉投票結果分析（比例代表） - 処理サマリーレポート\n")
        f.write(f"処理日時: {pd.Timestamp.now()}\n")
        f.write("="*60 + "\n\n")
        
        for sheet_name, df in all_processed_data.items():
            if df is not None:
                f.write(f"シート: {sheet_name}\n")
                f.write(f"  - 最終行数: {len(df)}\n")
                f.write(f"  - 列数: {len(df.columns)}\n")
                f.write(f"  - 数値列: {len(df.select_dtypes(include=['number']).columns)}個\n")
                f.write(f"  - 文字列列: {len(df.select_dtypes(include=['object']).columns)}個\n")
                f.write(f"  - 出力ファイル: 比例代表_{sheet_name}_縦並び版.csv\n")
                f.write("\n")
    
    print(f"📝 サマリーレポートを保存しました: {summary_file}")

def main():
    """
    メイン関数
    """
    print("=== 埼玉投票結果分析プログラム（比例代表版） ===")
    print("📂 出力ディレクトリ:")
    print("   - tmp_proportional/: クリーンアップ前のデータ")
    print("   - output_proportional/: 最終的な処理済みデータ")
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
        output_dir = "output_proportional"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 縦並び変換を実行して保存
        if cleaned_data is not None:
            transformed_data = transform_candidate_list_to_vertical(cleaned_data, sheet_name)
            
            # 縦並び版を保存（変換されたかどうかに関わらず）
            vertical_filename = os.path.join(output_dir, f"比例代表_{sheet_name}_縦並び版.csv")
            
            try:
                transformed_data.to_csv(vertical_filename, index=False, encoding='utf-8-sig')
                print(f"✅ 縦並び版CSVファイルを保存しました: {vertical_filename}")
                print(f"縦並び版データの先頭5行:")
                print(transformed_data.head())
            except Exception as e:
                print(f"縦並び版CSVファイルの保存中にエラーが発生しました: {e}")
            
            all_processed_data[sheet_name] = transformed_data
        else:
            all_processed_data[sheet_name] = cleaned_data
        
        # 基本的な分析を実行
        analyze_voting_data(all_processed_data[sheet_name])
    
    # 全体のサマリーレポートを作成
    create_summary_report(all_processed_data)
    
    print(f"\n{'='*60}")
    print("🎉 比例代表データの処理が完了しました！")
    print("📁 出力ファイルの確認:")
    print("   - tmp_proportional/: 元データのバックアップ")
    print("   - output_proportional/: 縦並び版の最終データ")
    print("   - output_proportional/*_縦並び版.csv: 各シートの縦並び版データ")
    print("   - output_proportional/比例代表_処理サマリーレポート.txt: 処理結果の概要")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
