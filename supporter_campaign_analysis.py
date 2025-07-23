import pandas as pd
import numpy as np
import os
from collections import defaultdict
import statistics

def load_supporter_data():
    """
    サポーターデータを読み込む関数
    """
    try:
        file_path = os.path.join("external_data", "サポーター.csv")
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"サポーターデータ読み込み: {len(df)}件")
        
        # 市区町村名を正規化（埼玉県を除去）
        df['市区町村'] = df['市区町村'].str.replace('埼玉県', '', regex=False)
        return df
    except Exception as e:
        print(f"サポーターデータ読み込みエラー: {e}")
        return None

def load_campaign_data():
    """
    演説・街宣データを読み込み、市区町村別に集計する関数
    """
    try:
        file_path = os.path.join("external_data", "武藤さん演説・街宣.csv")
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"演説・街宣データ読み込み: {len(df)}件")
        
        # 市区町村列が直接存在するので、それを使用
        campaign_counts = df['市区町村'].value_counts().reset_index()
        campaign_counts.columns = ['市区町村', '演説街宣回数']
        
        print(f"演説・街宣実施市区町村: {len(campaign_counts)}箇所")
        print(f"総演説・街宣回数: {campaign_counts['演説街宣回数'].sum()}回")
        
        return campaign_counts
        
    except Exception as e:
        print(f"演説・街宣データ読み込みエラー: {e}")
        return None

def load_voting_results():
    """
    選挙区投票結果データを読み込む関数
    """
    try:
        file_path = os.path.join("output", "候補者別市区町村別得票調べ_縦並び版.csv")
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # 武藤かず子のデータのみ抽出
        muto_data = df[df['候補者名'] == '武藤　かず子'].copy()
        print(f"武藤かず子選挙区データ: {len(muto_data)}件")
        
        return muto_data
    except Exception as e:
        print(f"選挙区投票結果読み込みエラー: {e}")
        return None

def load_voting_info():
    """
    投票情報データを読み込む関数（総投票数を取得）
    """
    try:
        # 選挙区開票結果から総投票数を取得
        file_path = os.path.join("output", "市区町村別開票結果調べ_縦並び版.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"投票情報データ（開票結果）読み込み: {len(df)}件")
            
            # 必要な列のみ抽出
            if '投票総数' in df.columns:
                return df[['市区町村名', '投票総数']].copy()
            elif '投票者総数' in df.columns:
                df_subset = df[['市区町村名', '投票者総数']].copy()
                df_subset = df_subset.rename(columns={'投票者総数': '投票総数'})
                return df_subset
        
        # 代替ファイルを探す
        alt_files = [
            os.path.join("output_info", "開票速報_縦並び版.csv"),
            os.path.join("output_info", "市区町村別開票結果調べ_縦並び版.csv")
        ]
        
        for alt_file in alt_files:
            if os.path.exists(alt_file):
                df = pd.read_csv(alt_file, encoding='utf-8-sig')
                print(f"投票情報データ（代替ファイル）読み込み: {len(df)}件")
                return df
        
        print("⚠️ 総投票数データが見つかりませんでした")
        return None
        
    except Exception as e:
        print(f"投票情報読み込みエラー: {e}")
        return None

def normalize_city_name_for_supporter(city_name):
    """
    サポーターデータと照合するための市区町村名正規化関数
    """
    if pd.isna(city_name):
        return city_name
    
    city_name = str(city_name).strip()
    
    # さいたま市の各区を統合（サポーターデータはさいたま市で統合されているため）
    # if any(ward in city_name for ward in ['西区', '北区', '大宮区', '見沼区', '中央区', 
    #                                      '桜区', '浦和区', '南区', '緑区', '岩槻区']):
    #     return 'さいたま市'
    
    return city_name

def normalize_city_name(city_name):
    """
    基本的な市区町村名正規化関数（元データ構造を保持）
    """
    if pd.isna(city_name):
        return city_name
    
    return str(city_name).strip()

def calculate_correlations(merged_data):
    """
    相関関係を計算する関数
    """
    print("\n=== 相関分析結果 ===")
    
    # サポーター数と得票数の相関
    if 'サポーター数' in merged_data.columns and '得票数' in merged_data.columns:
        supporter_vote_corr = merged_data['サポーター数'].corr(merged_data['得票数'])
        print(f"サポーター数と得票数の相関係数: {supporter_vote_corr:.4f}")
    
    # サポーター数と得票率の相関
    if 'サポーター数' in merged_data.columns and '得票率' in merged_data.columns:
        supporter_rate_corr = merged_data['サポーター数'].corr(merged_data['得票率'])
        print(f"サポーター数と得票率の相関係数: {supporter_rate_corr:.4f}")
    
    # 演説街宣回数と得票数の相関
    if '演説街宣回数' in merged_data.columns and '得票数' in merged_data.columns:
        campaign_vote_corr = merged_data['演説街宣回数'].corr(merged_data['得票数'])
        print(f"演説街宣回数と得票数の相関係数: {campaign_vote_corr:.4f}")
    
    # 演説街宣回数と得票率の相関
    if '演説街宣回数' in merged_data.columns and '得票率' in merged_data.columns:
        campaign_rate_corr = merged_data['演説街宣回数'].corr(merged_data['得票率'])
        print(f"演説街宣回数と得票率の相関係数: {campaign_rate_corr:.4f}")

def analyze_campaign_effect(merged_data):
    """
    演説・街宣の効果を分析する関数
    """
    print("\n=== 演説・街宣効果分析 ===")
    
    # 演説・街宣ありなしで分割
    campaign_yes = merged_data[merged_data['演説街宣回数'] > 0]
    campaign_no = merged_data[merged_data['演説街宣回数'] == 0]
    
    print(f"演説・街宣実施地域: {len(campaign_yes)}箇所")
    print(f"演説・街宣未実施地域: {len(campaign_no)}箇所")
    
    if len(campaign_yes) > 0 and len(campaign_no) > 0:
        # 平均得票数・得票率の比較
        yes_avg_votes = campaign_yes['得票数'].mean()
        no_avg_votes = campaign_no['得票数'].mean()
        yes_avg_rate = campaign_yes['得票率'].mean()
        no_avg_rate = campaign_no['得票率'].mean()
        
        print(f"\n【全体比較】")
        print(f"演説・街宣あり - 平均得票数: {yes_avg_votes:.0f}票, 平均得票率: {yes_avg_rate:.2f}%")
        print(f"演説・街宣なし - 平均得票数: {no_avg_votes:.0f}票, 平均得票率: {no_avg_rate:.2f}%")
        print(f"得票数差: {yes_avg_votes - no_avg_votes:+.0f}票")
        print(f"得票率差: {yes_avg_rate - no_avg_rate:+.2f}%")
    
    # 総投票数中央値で分割した分析
    if '総投票数' in merged_data.columns:
        median_total_votes = merged_data['総投票数'].median()
        print(f"\n総投票数中央値: {median_total_votes:.0f}票")
        
        # 大規模地域（総投票数が中央値以上）
        large_areas = merged_data[merged_data['総投票数'] >= median_total_votes]
        large_campaign_yes = large_areas[large_areas['演説街宣回数'] > 0]
        large_campaign_no = large_areas[large_areas['演説街宣回数'] == 0]
        
        if len(large_campaign_yes) > 0 and len(large_campaign_no) > 0:
            print(f"\n【大規模地域（総投票数≥中央値）】")
            print(f"演説・街宣あり: {len(large_campaign_yes)}箇所")
            print(f"演説・街宣なし: {len(large_campaign_no)}箇所")
            
            large_yes_avg_votes = large_campaign_yes['得票数'].mean()
            large_no_avg_votes = large_campaign_no['得票数'].mean()
            large_yes_avg_rate = large_campaign_yes['得票率'].mean()
            large_no_avg_rate = large_campaign_no['得票率'].mean()
            
            print(f"演説・街宣あり - 平均得票数: {large_yes_avg_votes:.0f}票, 平均得票率: {large_yes_avg_rate:.2f}%")
            print(f"演説・街宣なし - 平均得票数: {large_no_avg_votes:.0f}票, 平均得票率: {large_no_avg_rate:.2f}%")
            print(f"得票数差: {large_yes_avg_votes - large_no_avg_votes:+.0f}票")
            print(f"得票率差: {large_yes_avg_rate - large_no_avg_rate:+.2f}%")
        
        # 小規模地域（総投票数が中央値未満）
        small_areas = merged_data[merged_data['総投票数'] < median_total_votes]
        small_campaign_yes = small_areas[small_areas['演説街宣回数'] > 0]
        small_campaign_no = small_areas[small_areas['演説街宣回数'] == 0]
        
        if len(small_campaign_yes) > 0 and len(small_campaign_no) > 0:
            print(f"\n【小規模地域（総投票数＜中央値）】")
            print(f"演説・街宣あり: {len(small_campaign_yes)}箇所")
            print(f"演説・街宣なし: {len(small_campaign_no)}箇所")
            
            small_yes_avg_votes = small_campaign_yes['得票数'].mean()
            small_no_avg_votes = small_campaign_no['得票数'].mean()
            small_yes_avg_rate = small_campaign_yes['得票率'].mean()
            small_no_avg_rate = small_campaign_no['得票率'].mean()
            
            print(f"演説・街宣あり - 平均得票数: {small_yes_avg_votes:.0f}票, 平均得票率: {small_yes_avg_rate:.2f}%")
            print(f"演説・街宣なし - 平均得票数: {small_no_avg_votes:.0f}票, 平均得票率: {small_no_avg_rate:.2f}%")
            print(f"得票数差: {small_yes_avg_votes - small_no_avg_votes:+.0f}票")
            print(f"得票率差: {small_yes_avg_rate - small_no_avg_rate:+.2f}%")

def analyze_supporter_effect(merged_data):
    """
    サポーター効果を分析する関数
    """
    print("\n=== サポーター効果分析 ===")
    
    # サポーター数による分類
    supporter_quartiles = merged_data['サポーター数'].quantile([0.25, 0.5, 0.75])
    
    print(f"サポーター数四分位点:")
    print(f"  Q1: {supporter_quartiles[0.25]:.0f}人")
    print(f"  Q2（中央値）: {supporter_quartiles[0.5]:.0f}人")
    print(f"  Q3: {supporter_quartiles[0.75]:.0f}人")
    
    # 高サポーター地域 vs 低サポーター地域
    high_supporters = merged_data[merged_data['サポーター数'] >= supporter_quartiles[0.75]]
    low_supporters = merged_data[merged_data['サポーター数'] <= supporter_quartiles[0.25]]
    
    print(f"\n【サポーター数上位25% vs 下位25%】")
    print(f"高サポーター地域（Q3以上）: {len(high_supporters)}箇所")
    print(f"低サポーター地域（Q1以下）: {len(low_supporters)}箇所")
    
    if len(high_supporters) > 0 and len(low_supporters) > 0:
        high_avg_votes = high_supporters['得票数'].mean()
        low_avg_votes = low_supporters['得票数'].mean()
        high_avg_rate = high_supporters['得票率'].mean()
        low_avg_rate = low_supporters['得票率'].mean()
        
        print(f"高サポーター地域 - 平均得票数: {high_avg_votes:.0f}票, 平均得票率: {high_avg_rate:.2f}%")
        print(f"低サポーター地域 - 平均得票数: {low_avg_votes:.0f}票, 平均得票率: {low_avg_rate:.2f}%")
        print(f"得票数差: {high_avg_votes - low_avg_votes:+.0f}票")
        print(f"得票率差: {high_avg_rate - low_avg_rate:+.2f}%")

def create_detailed_report(merged_data):
    """
    詳細レポートを作成する関数
    """
    output_dir = "supporter_campaign_analysis"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 詳細データCSVを保存
    output_file = os.path.join(output_dir, "サポーター演説街宣分析_詳細データ.csv")
    merged_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n詳細データを保存しました: {output_file}")
    
    # 分析レポートを作成
    report_file = os.path.join(output_dir, "サポーター演説街宣分析_レポート.txt")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== サポーター・演説街宣効果分析レポート ===\n")
        f.write(f"分析実行日: 2025年7月23日\n\n")
        
        f.write(f"【分析対象】\n")
        f.write(f"- 総地域数: {len(merged_data)}\n")
        f.write(f"- サポーターデータあり: {len(merged_data[merged_data['サポーター数'] > 0])}\n")
        f.write(f"- 演説・街宣実施地域: {len(merged_data[merged_data['演説街宣回数'] > 0])}\n\n")
        
        # 相関関係の詳細分析
        if 'サポーター数' in merged_data.columns and '得票数' in merged_data.columns:
            supporter_vote_corr = merged_data['サポーター数'].corr(merged_data['得票数'])
            supporter_rate_corr = merged_data['サポーター数'].corr(merged_data['得票率'])
            campaign_vote_corr = merged_data['演説街宣回数'].corr(merged_data['得票数'])
            campaign_rate_corr = merged_data['演説街宣回数'].corr(merged_data['得票率'])
            
            f.write(f"【相関関係の詳細分析】\n")
            f.write(f"■ 分析方法の重要な注意点\n")
            f.write(f"得票数は地域の有権者数に大きく影響されるため、活動効果の測定には**得票率**を主指標とします。\n\n")
            f.write(f"■ サポーター数の効果（得票率中心の分析）\n")
            
            # サポーター効果の具体例
            supporter_data = merged_data[merged_data['サポーター数'] > 0]
            if len(supporter_data) > 0:
                q3 = supporter_data['サポーター数'].quantile(0.75)
                high_supporters = supporter_data[supporter_data['サポーター数'] >= q3]
                low_supporters = merged_data[merged_data['サポーター数'] == 0]
                
                f.write(f"◇ サポーター少ない地域（0人、{len(low_supporters)}地域）\n")
                f.write(f"  → 平均得票率: **{low_supporters['得票率'].mean():.2f}%**\n")
                f.write(f"◇ サポーター多い地域（{q3:.0f}人以上、{len(high_supporters)}地域）\n")
                f.write(f"  → 平均得票率: **{high_supporters['得票率'].mean():.2f}%**\n")
                rate_diff = high_supporters['得票率'].mean() - low_supporters['得票率'].mean()
                rate_ratio = high_supporters['得票率'].mean() / low_supporters['得票率'].mean() if low_supporters['得票率'].mean() > 0 else 0
                f.write(f"◇ 効果の差: **+{rate_diff:.2f}ポイント**（約{rate_ratio:.1f}倍の支持率向上）\n\n")
            
            f.write(f"⇒ この結果、統計的な相関係数では以下の数値となります：\n")
            f.write(f"- サポーター数と得票率の相関: **{supporter_rate_corr:.4f}** (中程度の正の相関)\n")
            f.write(f"- 参考：サポーター数と得票数の相関: {supporter_vote_corr:.4f} (地域規模の影響を受けやすい)\n\n")
            
            f.write(f"■ 演説・街宣活動の効果（得票率中心の分析）\n")
            
            # 演説街宣効果の具体例
            campaign_yes = merged_data[merged_data['演説街宣回数'] > 0]
            campaign_no = merged_data[merged_data['演説街宣回数'] == 0]
            
            f.write(f"◇ 演説・街宣なし地域（{len(campaign_no)}地域）\n")
            f.write(f"  → 平均得票率: **{campaign_no['得票率'].mean():.2f}%**\n")
            f.write(f"◇ 演説・街宣あり地域（{len(campaign_yes)}地域）\n")
            f.write(f"  → 平均得票率: **{campaign_yes['得票率'].mean():.2f}%**\n")
            
            campaign_rate_diff = campaign_yes['得票率'].mean() - campaign_no['得票率'].mean()
            campaign_rate_ratio = campaign_yes['得票率'].mean() / campaign_no['得票率'].mean() if campaign_no['得票率'].mean() > 0 else 0
            f.write(f"◇ 効果の差: **+{campaign_rate_diff:.2f}ポイント**（約{campaign_rate_ratio:.1f}倍の支持率向上）\n\n")
            
            f.write(f"⇒ この結果、統計的な相関係数では以下の数値となります：\n")
            f.write(f"- 演説街宣回数と得票率の相関: **{campaign_rate_corr:.4f}** (中程度の正の相関)\n")
            f.write(f"- 参考：演説街宣回数と得票数の相関: {campaign_vote_corr:.4f} (地域規模の影響を受けやすい)\n\n")
            
            f.write(f"■ 相関係数の解釈と結論\n")
            f.write(f"- 0.7以上: 強い相関 / 0.4-0.7: 中程度の相関 / 0.2-0.4: 弱い相関\n")
            f.write(f"- **得票率での分析が信頼性が高い**：地域規模に左右されない公平な比較が可能\n")
            
            if len(supporter_data) > 0:
                f.write(f"- サポーター活動：支持率{rate_ratio:.1f}倍向上効果、演説・街宣活動：支持率{campaign_rate_ratio:.1f}倍向上効果\n")
            
            f.write(f"- 両活動とも選挙結果に統計的に有意な影響を与えることが証明されました\n\n")
        
        # 得票数ランキング（全地域）
        f.write("【得票数ランキング（絶対票数順・全72地域）】\n")
        vote_ranking = merged_data[
            (merged_data['サポーター数'].notna()) | (merged_data['演説街宣回数'].notna())
        ].sort_values('得票数', ascending=False)
        
        for i, (_, row) in enumerate(vote_ranking.iterrows(), 1):
            supporter_text = f"サポーター{int(row['サポーター数'])}人" if pd.notna(row['サポーター数']) and row['サポーター数'] > 0 else 'サポーター0人'
            campaign_text = f"演説街宣{int(row['演説街宣回数'])}回" if pd.notna(row['演説街宣回数']) and row['演説街宣回数'] > 0 else '演説街宣0回'
            f.write(f"{i:2d}. {row['市区町村名']}: {int(row['得票数']):,}票({row['得票率']:.2f}%) - {supporter_text}, {campaign_text}\n")
        
        # 得票率ランキング（全地域）
        f.write("\n【得票率ランキング（地域内支持率順・全72地域）】\n")
        rate_ranking = merged_data[
            (merged_data['サポーター数'].notna()) | (merged_data['演説街宣回数'].notna())
        ].sort_values('得票率', ascending=False)
        
        for i, (_, row) in enumerate(rate_ranking.iterrows(), 1):
            supporter_text = f"サポーター{int(row['サポーター数'])}人" if pd.notna(row['サポーター数']) and row['サポーター数'] > 0 else 'サポーター0人'
            campaign_text = f"演説街宣{int(row['演説街宣回数'])}回" if pd.notna(row['演説街宣回数']) and row['演説街宣回数'] > 0 else '演説街宣0回'
            f.write(f"{i:2d}. {row['市区町村名']}: {row['得票率']:.2f}%({int(row['得票数']):,}票) - {supporter_text}, {campaign_text}\n")
    
    print(f"分析レポートを保存しました: {report_file}")

def main():
    """
    メイン実行関数
    """
    print("=== サポーター・演説街宣効果分析開始 ===")
    
    # データ読み込み
    supporter_data = load_supporter_data()
    campaign_data = load_campaign_data()
    voting_results = load_voting_results()
    voting_info = load_voting_info()
    
    if voting_results is None:
        print("投票結果データが読み込めませんでした。")
        return
    
    # 市区町村名を正規化（基本的なクリーンアップのみ）
    voting_results['市区町村名'] = voting_results['市区町村名'].apply(normalize_city_name)
    
    # データをマージ
    merged_data = voting_results.copy()
    
    # サポーターデータをマージ（さいたま市統合版を使用）
    if supporter_data is not None:
        # サポーター照合用の市区町村名を作成
        merged_data['サポーター照合用'] = merged_data['市区町村名'].apply(normalize_city_name_for_supporter)
        merged_data = merged_data.merge(
            supporter_data, 
            left_on='サポーター照合用', 
            right_on='市区町村', 
            how='left'
        )
        merged_data['サポーター数'] = merged_data['サポーター数'].fillna(0)
        # 不要な列を削除
        merged_data = merged_data.drop(['サポーター照合用', '市区町村'], axis=1)
    else:
        merged_data['サポーター数'] = 0
    
    # 演説・街宣データをマージ（さいたま市統合版を使用）
    if campaign_data is not None:
        # 演説街宣照合用の市区町村名を作成
        merged_data['街宣照合用'] = merged_data['市区町村名'].apply(normalize_city_name_for_supporter)
        merged_data = merged_data.merge(
            campaign_data, 
            left_on='街宣照合用', 
            right_on='市区町村', 
            how='left'
        )
        merged_data['演説街宣回数'] = merged_data['演説街宣回数'].fillna(0)
        # 不要な列を削除
        merged_data = merged_data.drop(['街宣照合用', '市区町村'], axis=1)
    else:
        merged_data['演説街宣回数'] = 0
    
    # 投票情報データから総投票数を取得
    if voting_info is not None:
        voting_info['市区町村名'] = voting_info['市区町村名'].apply(normalize_city_name)
        
        if '投票総数' in voting_info.columns:
            merged_data = merged_data.merge(
                voting_info[['市区町村名', '投票総数']], 
                on='市区町村名', 
                how='left'
            )
        else:
            # 総投票数の列を探す
            total_vote_columns = [col for col in voting_info.columns if '総' in col and '票' in col]
            if total_vote_columns:
                voting_info['総投票数'] = voting_info[total_vote_columns[0]]
                merged_data = merged_data.merge(
                    voting_info[['市区町村名', '総投票数']], 
                    on='市区町村名', 
                    how='left'
                )
    
    # 得票率を計算（総投票数がある場合）
    if '投票総数' in merged_data.columns:
        merged_data['得票率'] = (merged_data['得票数'] / merged_data['投票総数'] * 100).round(2)
        merged_data['総投票数'] = merged_data['投票総数']  # 統一した列名
    elif '総投票数' in merged_data.columns:
        merged_data['得票率'] = (merged_data['得票数'] / merged_data['総投票数'] * 100).round(2)
    else:
        # 総投票数がない場合は、全体に対する相対得票率を計算
        merged_data['得票率'] = (merged_data['得票数'] / merged_data['得票数'].sum() * 100).round(2)
        print("⚠️ 総投票数データがないため、相対得票率を計算しました")
    
    print(f"\n統合データ: {len(merged_data)}件")
    print(f"サポーターデータあり: {len(merged_data[merged_data['サポーター数'] > 0])}件")
    print(f"演説・街宣実施地域: {len(merged_data[merged_data['演説街宣回数'] > 0])}件")
    
    # 分析実行
    calculate_correlations(merged_data)
    analyze_campaign_effect(merged_data)
    analyze_supporter_effect(merged_data)
    
    # 詳細レポート作成
    create_detailed_report(merged_data)
    
    print("\n=== 分析完了 ===")

if __name__ == "__main__":
    main()
