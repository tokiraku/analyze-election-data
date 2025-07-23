import pandas as pd
import os
from datetime import datetime

def load_candidate_data():
    """
    既存のCSVファイルから候補者データを読み込み
    """
    candidates_file = "output/候補者別市区町村別得票調べ_縦並び版.csv"
    voting_info_file = "output_info/選挙区_投票調べ（国内＋在外）_最終版.csv"
    
    if not os.path.exists(candidates_file):
        print(f"エラー: {candidates_file} が見つかりません")
        return None, None
    
    if not os.path.exists(voting_info_file):
        print(f"エラー: {voting_info_file} が見つかりません")
        return None, None
    
    # 候補者データを読み込み
    candidates_df = pd.read_csv(candidates_file, encoding='utf-8')
    
    # 投票情報データを読み込み
    voting_info_df = pd.read_csv(voting_info_file, encoding='utf-8')
    
    return candidates_df, voting_info_df

def extract_candidate_electoral_data(candidates_df, voting_info_df, candidate_name):
    """
    CSVデータから指定候補者の情報を抽出（総投票数付き）
    """
    # 候補者データをフィルタ
    candidate_data = candidates_df[candidates_df['候補者名'] == candidate_name].copy()
    
    if candidate_data.empty:
        print(f"候補者 {candidate_name} のデータが見つかりません")
        return []
    
    # 投票情報とマージして総投票数を取得
    merged_data = candidate_data.merge(
        voting_info_df[['市区町村名', '投票者数計']], 
        on='市区町村名', 
        how='left'
    )
    
    # 得票率を計算
    merged_data['得票率'] = (merged_data['得票数'] / merged_data['投票者数計']) * 100
    
    # 結果を辞書のリストに変換
    electoral_data = []
    for _, row in merged_data.iterrows():
        electoral_data.append({
            'municipality': row['市区町村名'],
            'candidate': row['候補者名'],
            'party': row['党派名等'],
            'votes': row['得票数'],
            'total_votes': row['投票者数計'],
            'vote_percentage': row['得票率']
        })
    
    return electoral_data

def generate_detailed_comparison_report(team_mirai_data, furukawa_data, ehara_data):
    """
    詳細な3候補者の比較レポートを生成
    """
    timestamp = datetime.now()
    
    report = f"""詳細選挙結果比較分析レポート（CSVベース）
作成日時: {timestamp}
======================================================================

【比較対象候補者】
• 武藤　かず子 (チームみらい(新)) - 新人
• 古川　俊治 (自由民主党(現)) - 現職
• 江原　くみ子 (国民民主党(新)) - 新人

"""
    
    if team_mirai_data and furukawa_data and ehara_data:
        # データフレーム作成
        tm_df = pd.DataFrame(team_mirai_data)
        fk_df = pd.DataFrame(furukawa_data)
        eh_df = pd.DataFrame(ehara_data)
        
        # 総得票数と得票率
        tm_total = tm_df['votes'].sum()
        fk_total = fk_df['votes'].sum()
        eh_total = eh_df['votes'].sum()
        
        # 総投票数（全候補者で統一）
        total_all_votes = tm_df['total_votes'].sum()
        
        tm_overall_rate = (tm_total / total_all_votes) * 100
        fk_overall_rate = (fk_total / total_all_votes) * 100
        eh_overall_rate = (eh_total / total_all_votes) * 100
        
        report += f"""【総合結果】
総得票数と得票率:
  1位: 古川　俊治 (自由民主党): {fk_total:,}票 ({fk_overall_rate:.2f}%)
  2位: 江原　くみ子 (国民民主党): {eh_total:,}票 ({eh_overall_rate:.2f}%)
  3位: 武藤　かず子 (チームみらい): {tm_total:,}票 ({tm_overall_rate:.2f}%)

得票差分析:
• 古川俊治との差: {fk_total - tm_total:,}票 (古川が{(fk_total / tm_total):.1f}倍の得票数)
• 江原くみ子との差: {eh_total - tm_total:,}票 (江原が{(eh_total / tm_total):.1f}倍の得票数)

"""
        
        # 得票率分析
        report += "【得票率統計分析】\n"
        
        # 各候補者の得票率統計
        for name, df in [("武藤　かず子", tm_df), ("古川　俊治", fk_df), ("江原　くみ子", eh_df)]:
            mean_rate = df['vote_percentage'].mean()
            median_rate = df['vote_percentage'].median()
            max_rate = df['vote_percentage'].max()
            min_rate = df['vote_percentage'].min()
            std_rate = df['vote_percentage'].std()
            
            total_votes = df['votes'].sum()
            total_all_votes = tm_df['total_votes'].sum()
            
            max_region = df.loc[df['vote_percentage'].idxmax(), 'municipality']
            min_region = df.loc[df['vote_percentage'].idxmin(), 'municipality']
            
            # 最高得票数と最低得票数の地域
            max_votes_region = df.loc[df['votes'].idxmax(), 'municipality']
            min_votes_region = df.loc[df['votes'].idxmin(), 'municipality']
            max_votes = df['votes'].max()
            min_votes = df['votes'].min()
            
            # 各地域の総投票数も取得
            max_rate_total_votes = df.loc[df['vote_percentage'].idxmax(), 'total_votes']
            min_rate_total_votes = df.loc[df['vote_percentage'].idxmin(), 'total_votes']
            max_votes_total_votes = df.loc[df['votes'].idxmax(), 'total_votes']
            min_votes_total_votes = df.loc[df['votes'].idxmin(), 'total_votes']
            
            report += f"{name}:\n"
            report += f"  総得票数: {total_votes:,}票\n"
            report += f"  総投票数: {total_all_votes:,}票\n"
            report += f"  全体得票率: {(total_votes / total_all_votes * 100):.2f}%\n"
            report += f"  平均得票率: {mean_rate:.2f}%\n"
            report += f"  中央値: {median_rate:.2f}%\n"
            report += f"  最高得票率: {max_rate:.2f}% ({max_region}) [総投票数: {max_rate_total_votes:,}票]\n"
            report += f"  最低得票率: {min_rate:.2f}% ({min_region}) [総投票数: {min_rate_total_votes:,}票]\n"
            report += f"  最高得票数: {max_votes:,}票 ({max_votes_region}) [総投票数: {max_votes_total_votes:,}票]\n"
            report += f"  最低得票数: {min_votes:,}票 ({min_votes_region}) [総投票数: {min_votes_total_votes:,}票]\n"
            report += f"  標準偏差: {std_rate:.2f}%\n\n"
        
        # 地域別競合分析
        report += "【地域別競合分析】\n"
        
        # 各地域での順位を計算
        combined_data = []
        for _, tm_row in tm_df.iterrows():
            municipality = tm_row['municipality']
            tm_votes = tm_row['votes']
            tm_rate = tm_row['vote_percentage']
            
            fk_votes = fk_df[fk_df['municipality'] == municipality]['votes'].iloc[0] if len(fk_df[fk_df['municipality'] == municipality]) > 0 else 0
            eh_votes = eh_df[eh_df['municipality'] == municipality]['votes'].iloc[0] if len(eh_df[eh_df['municipality'] == municipality]) > 0 else 0
            
            fk_rate = fk_df[fk_df['municipality'] == municipality]['vote_percentage'].iloc[0] if len(fk_df[fk_df['municipality'] == municipality]) > 0 else 0
            eh_rate = eh_df[eh_df['municipality'] == municipality]['vote_percentage'].iloc[0] if len(eh_df[eh_df['municipality'] == municipality]) > 0 else 0
            
            # 順位を決定
            votes_list = [(tm_votes, 'チームみらい', tm_rate), (fk_votes, '自民党', fk_rate), (eh_votes, '国民民主', eh_rate)]
            votes_list.sort(key=lambda x: x[0], reverse=True)
            
            tm_rank = next((i+1 for i, (votes, party, rate) in enumerate(votes_list) if party == 'チームみらい'), 4)
            
            combined_data.append({
                'municipality': municipality,
                'tm_votes': tm_votes,
                'tm_rate': tm_rate,
                'tm_rank': tm_rank,
                'fk_rate': fk_rate,
                'eh_rate': eh_rate,
                'min_diff': min(abs(tm_rate - fk_rate), abs(tm_rate - eh_rate))
            })
        
        combined_df = pd.DataFrame(combined_data)
        
        # 順位分布
        rank_counts = combined_df['tm_rank'].value_counts().sort_index()
        report += "チームみらいの地域別順位分布:\n"
        for rank in [1, 2, 3]:
            count = rank_counts.get(rank, 0)
            percentage = (count / len(combined_df)) * 100
            report += f"  {rank}位獲得地域: {count}地域 ({percentage:.1f}%)\n"
        
        report += "\n【チームみらいの健闘地域分析】\n"
        
        # 得票率順にソート
        sorted_combined = combined_df.sort_values('tm_rate', ascending=False)
        
        report += "全地域得票率降順:\n"
        for i, (_, row) in enumerate(sorted_combined.iterrows(), 1):
            report += f"  {i:2d}. {row['municipality']}: {row['tm_rate']:.2f}% ({row['tm_votes']:,}票) [順位: {row['tm_rank']}位]\n"
            report += f"      古川: {row['fk_rate']:.2f}%, 江原: {row['eh_rate']:.2f}%\n"
        
        report += "\n【激戦地域分析】\n"
        
        # 最小差順にソート
        sorted_by_diff = combined_df.sort_values('min_diff', ascending=True)
        
        report += "他候補との得票率差が最小だった地域（全地域降順）:\n"
        for i, (_, row) in enumerate(sorted_by_diff.iterrows(), 1):
            report += f"  {i:2d}. {row['municipality']}: 最小差{row['min_diff']:.2f}%\n"
            report += f"     チームみらい: {row['tm_rate']:.2f}%, 古川: {row['fk_rate']:.2f}%, 江原: {row['eh_rate']:.2f}%\n"
        
    report += "\n" + "="*70 + "\n詳細比較分析完了（CSVベース）\n"
    return report

def main():
    print("詳細選挙結果比較分析を開始します（CSVベース）...")
    
    # CSVファイルからデータを読み込み
    candidates_df, voting_info_df = load_candidate_data()
    
    if candidates_df is None or voting_info_df is None:
        print("データの読み込みに失敗しました")
        return
    
    print("=== 武藤　かず子 のデータ抽出中 ===")
    team_mirai_data = extract_candidate_electoral_data(candidates_df, voting_info_df, '武藤　かず子')
    
    print("=== 古川　俊治 のデータ抽出中 ===")
    furukawa_data = extract_candidate_electoral_data(candidates_df, voting_info_df, '古川　俊治')
    
    print("=== 江原　くみ子 のデータ抽出中 ===")
    ehara_data = extract_candidate_electoral_data(candidates_df, voting_info_df, '江原　くみ子')
    
    # レポート生成
    report = generate_detailed_comparison_report(team_mirai_data, furukawa_data, ehara_data)
    
    # 出力ディレクトリを作成
    output_dir = "comparison_analysis"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # ファイルに保存
    output_file = os.path.join(output_dir, "詳細候補者比較分析レポート_CSVベース.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"詳細比較分析レポートが生成されました: {output_file}")
    print("="*70)
    print(report)

if __name__ == "__main__":
    main()
