#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
チームみらい（武藤かず子）詳細分析スクリプト
選挙区データを使用してチームみらいの詳細な選挙分析を実行
"""

import pandas as pd
import os
from datetime import datetime
import numpy as np

def load_candidate_data():
    """候補者データを読み込む"""
    try:
        df = pd.read_csv('output/候補者別市区町村別得票調べ_縦並び版.csv', encoding='utf-8')
        print(f"候補者データを読み込みました: {len(df)}行")
        return df
    except Exception as e:
        print(f"候補者データの読み込みエラー: {e}")
        return None

def load_voting_results():
    """投票結果データを読み込む"""
    try:
        df = pd.read_csv('output/市区町村別開票結果調べ_縦並び版.csv', encoding='utf-8')
        print(f"投票結果データを読み込みました: {len(df)}行")
        return df
    except Exception as e:
        print(f"投票結果データの読み込みエラー: {e}")
        return None

def load_voting_info():
    """投票情報データを読み込む"""
    try:
        df = pd.read_csv('output_info/選挙区_投票調べ（国内＋在外）_最終版.csv', encoding='utf-8')
        print(f"投票情報データを読み込みました: {len(df)}行")
        return df
    except Exception as e:
        print(f"投票情報データの読み込みエラー: {e}")
        return None

def load_proportional_data():
    """比例データを読み込む"""
    try:
        # 比例代表の政党別得票データを読み込み
        proportional_df = pd.read_csv('output_proportional/比例代表_得票総数の開票区別政党等別一覧_縦並び版.csv', encoding='utf-8')
        results_df = pd.read_csv('output_proportional/比例代表_開票結果調べ_縦並び版.csv', encoding='utf-8')
        print(f"比例政党別データを読み込みました: {len(proportional_df)}行")
        print(f"比例結果データを読み込みました: {len(results_df)}行")
        return proportional_df, results_df
    except Exception as e:
        print(f"比例データの読み込みエラー: {e}")
        return None, None

def extract_team_mirai_data(df):
    """チームみらいのデータを抽出"""
    team_mirai = df[df['候補者名'] == '武藤　かず子'].copy()
    print(f"チームみらいデータを抽出しました: {len(team_mirai)}行")
    
    # 得票数を数値に変換
    team_mirai['得票数'] = pd.to_numeric(team_mirai['得票数'], errors='coerce')
    
    return team_mirai

def analyze_proportional_performance(proportional_df, proportional_results_df):
    """比例でのチームみらい分析"""
    analysis = {}
    
    if proportional_df is None:
        return analysis
    
    # ファイルの構造を確認
    print(f"比例データの列名: {list(proportional_df.columns)}")
    if len(proportional_df) > 0:
        print(f"比例データの先頭5行:\n{proportional_df.head()}")
    
    # チームみらい関連の政党を検索（実際の列名を使用）
    team_mirai_data = None
    
    # 実際の列名に基づいて処理（'政党等名'列を使用）
    if '政党等名' in proportional_df.columns:
        team_mirai_data = proportional_df[proportional_df['政党等名'].str.contains('チームみらい|みらい', na=False, case=False)].copy()
        region_col, party_col, votes_col = '開票区', '政党等名', '得票数'
    elif '政党名' in proportional_df.columns:
        team_mirai_data = proportional_df[proportional_df['政党名'].str.contains('チームみらい|みらい', na=False, case=False)].copy()
        region_col, party_col, votes_col = proportional_df.columns[0], '政党名', proportional_df.columns[-1]
    elif len(proportional_df.columns) >= 2:  # 市区町村名, 政党名, 得票数の形式を想定
        col_names = proportional_df.columns.tolist()
        if len(col_names) >= 3:
            # [市区町村名, 政党名, 得票数] の形式を想定
            region_col, party_col, votes_col = col_names[0], col_names[1], col_names[2]
            team_mirai_data = proportional_df[proportional_df[party_col].str.contains('チームみらい|みらい', na=False, case=False)].copy()
        
    if team_mirai_data is None or team_mirai_data.empty:
        print("比例でチームみらい関連の政党が見つかりませんでした")
        return analysis
    
    print(f"比例でチームみらいデータを発見: {len(team_mirai_data)}行")
    
    # 数値変換
    team_mirai_data[votes_col] = pd.to_numeric(team_mirai_data[votes_col], errors='coerce')
    
    # 選挙区データと比較して、欠けている地域を0票として追加
    if proportional_results_df is not None:
        # 全ての地域を取得
        all_regions = set(proportional_results_df[
            ~proportional_results_df['市区町村等'].str.contains('計|県　', na=False)
        ]['市区町村等'].unique())
        
        # 現在のチームみらいデータの地域
        current_regions = set(team_mirai_data[region_col].unique())
        
        # 欠けている地域
        missing_regions = all_regions - current_regions
        
        if missing_regions:
            print(f"欠けている地域を0票として追加: {sorted(missing_regions)}")
            
            # 欠けている地域を0票として追加
            missing_data = []
            for region in missing_regions:
                missing_data.append({
                    region_col: region,
                    party_col: 'チームみらい',
                    votes_col: 0
                })
            
            if missing_data:
                missing_df = pd.DataFrame(missing_data)
                team_mirai_data = pd.concat([team_mirai_data, missing_df], ignore_index=True)
                print(f"追加後のチームみらいデータ: {len(team_mirai_data)}行")
    
    # 基本統計
    analysis['total_votes'] = team_mirai_data[votes_col].sum()
    analysis['regions_count'] = len(team_mirai_data)
    analysis['avg_votes'] = team_mirai_data[votes_col].mean()
    analysis['median_votes'] = team_mirai_data[votes_col].median()
    analysis['std_votes'] = team_mirai_data[votes_col].std()
    
    # 最高・最低得票数
    max_votes_idx = team_mirai_data[votes_col].idxmax()
    min_votes_idx = team_mirai_data[votes_col].idxmin()
    
    analysis['max_votes_region'] = team_mirai_data.loc[max_votes_idx, region_col]
    analysis['max_votes_count'] = team_mirai_data.loc[max_votes_idx, votes_col]
    analysis['min_votes_region'] = team_mirai_data.loc[min_votes_idx, region_col]
    analysis['min_votes_count'] = team_mirai_data.loc[min_votes_idx, votes_col]
    
    # 得票率計算（比例結果データとマージ）
    if proportional_results_df is not None:
        # 比例結果データの列名確認
        print(f"比例結果データの列名: {list(proportional_results_df.columns)}")
        
        # 比例結果データから市区町村レベルのデータのみを抽出（集計行を除外）
        results_filtered = proportional_results_df[
            ~proportional_results_df['市区町村等'].str.contains('計|県　', na=False)
        ].copy()
        
        print(f"フィルタ後の比例結果データ: {len(results_filtered)}行")
        
        # 数値列を確認して変換
        if '有効投票数' in results_filtered.columns:
            results_filtered['有効投票数'] = pd.to_numeric(results_filtered['有効投票数'], errors='coerce')
        
        # 地域名でマージ
        merged = team_mirai_data.merge(
            results_filtered, 
            left_on=region_col, 
            right_on='市区町村等', 
            how='left'
        )
        
        print(f"マージ後のデータ: {len(merged)}行")
        
        if '有効投票数' in merged.columns and not merged['有効投票数'].isna().all():
            merged['得票率'] = (merged[votes_col] / merged['有効投票数']) * 100
            analysis['avg_rate'] = merged['得票率'].mean()
            analysis['median_rate'] = merged['得票率'].median()
            analysis['std_rate'] = merged['得票率'].std()
            analysis['total_valid_votes'] = merged['有効投票数'].sum()
            analysis['overall_rate'] = (analysis['total_votes'] / analysis['total_valid_votes']) * 100
            
            # 得票率が最高・最低の地域
            max_rate_idx = merged['得票率'].idxmax()
            min_rate_idx = merged['得票率'].idxmin()
            
            analysis['max_rate_region'] = merged.loc[max_rate_idx, region_col]
            analysis['max_rate_value'] = merged.loc[max_rate_idx, '得票率']
            analysis['max_rate_total_votes'] = merged.loc[max_rate_idx, '有効投票数']
            
            analysis['min_rate_region'] = merged.loc[min_rate_idx, region_col]
            analysis['min_rate_value'] = merged.loc[min_rate_idx, '得票率']
            analysis['min_rate_total_votes'] = merged.loc[min_rate_idx, '有効投票数']
            
            # 詳細データも保存
            analysis['detailed_data'] = merged[[region_col, votes_col, '得票率', '有効投票数']].copy()
            analysis['detailed_data'].columns = ['市区町村名', '得票数', '得票率', '有効投票数']
        else:
            print("警告: 有効投票数データが利用できませんでした")
    
    return analysis

def analyze_team_mirai_performance(team_mirai_data, voting_results, voting_info):
    """チームみらいのパフォーマンス分析"""
    analysis = {}
    
    # 基本統計
    analysis['total_votes'] = team_mirai_data['得票数'].sum()
    analysis['regions_count'] = len(team_mirai_data)
    analysis['avg_votes'] = team_mirai_data['得票数'].mean()
    analysis['median_votes'] = team_mirai_data['得票数'].median()
    analysis['std_votes'] = team_mirai_data['得票数'].std()
    
    # 最高・最低得票数
    max_votes_idx = team_mirai_data['得票数'].idxmax()
    min_votes_idx = team_mirai_data['得票数'].idxmin()
    
    analysis['max_votes_region'] = team_mirai_data.loc[max_votes_idx, '市区町村名']
    analysis['max_votes_count'] = team_mirai_data.loc[max_votes_idx, '得票数']
    analysis['min_votes_region'] = team_mirai_data.loc[min_votes_idx, '市区町村名']
    analysis['min_votes_count'] = team_mirai_data.loc[min_votes_idx, '得票数']
    
    # 得票率分析（投票結果データとマージして計算）
    if voting_results is not None:
        # 数値列を確認して変換
        numeric_cols = ['有効投票総数', '投票総数', '投票者総数']
        for col in numeric_cols:
            if col in voting_results.columns:
                voting_results[col] = pd.to_numeric(voting_results[col], errors='coerce')
        
        merged = team_mirai_data.merge(voting_results, on='市区町村名', how='left')
        
        if '有効投票総数' in merged.columns:
            merged['得票率'] = (merged['得票数'] / merged['有効投票総数']) * 100
            analysis['avg_vote_rate'] = merged['得票率'].mean()
            analysis['median_vote_rate'] = merged['得票率'].median()
            analysis['std_vote_rate'] = merged['得票率'].std()
            
            # 得票率が最高・最低の地域
            max_rate_idx = merged['得票率'].idxmax()
            min_rate_idx = merged['得票率'].idxmin()
            
            analysis['max_rate_region'] = merged.loc[max_rate_idx, '市区町村名']
            analysis['max_rate_value'] = merged.loc[max_rate_idx, '得票率']
            analysis['max_rate_total_votes'] = merged.loc[max_rate_idx, '有効投票総数']
            
            analysis['min_rate_region'] = merged.loc[min_rate_idx, '市区町村名']
            analysis['min_rate_value'] = merged.loc[min_rate_idx, '得票率']
            analysis['min_rate_total_votes'] = merged.loc[min_rate_idx, '有効投票総数']
            
            # 全体の得票率
            total_valid_votes = merged['有効投票総数'].sum()
            analysis['overall_vote_rate'] = (analysis['total_votes'] / total_valid_votes) * 100
            
            # 得票率別地域分類
            analysis['high_performance_regions'] = merged[merged['得票率'] >= 3.0]['市区町村名'].tolist()
            analysis['medium_performance_regions'] = merged[(merged['得票率'] >= 2.0) & (merged['得票率'] < 3.0)]['市区町村名'].tolist()
            analysis['low_performance_regions'] = merged[merged['得票率'] < 2.0]['市区町村名'].tolist()
        else:
            print("警告: 有効投票総数データが見つかりません")
    
    return analysis, merged if 'merged' in locals() else team_mirai_data

def analyze_regional_patterns(team_mirai_data):
    """地域パターンの分析"""
    patterns = {}
    
    # さいたま市内の分析
    saitama_regions = team_mirai_data[team_mirai_data['市区町村名'].str.contains('さいたま市', na=False)]
    if not saitama_regions.empty:
        patterns['saitama_total_votes'] = saitama_regions['得票数'].sum()
        patterns['saitama_regions_count'] = len(saitama_regions)
        patterns['saitama_avg_votes'] = saitama_regions['得票数'].mean()
        patterns['saitama_regions'] = saitama_regions[['市区町村名', '得票数']].to_dict('records')
    
    # 市部と町村部の比較
    city_regions = team_mirai_data[team_mirai_data['市区町村名'].str.contains('市', na=False)]
    town_regions = team_mirai_data[~team_mirai_data['市区町村名'].str.contains('市', na=False)]
    
    if not city_regions.empty:
        patterns['city_total_votes'] = city_regions['得票数'].sum()
        patterns['city_regions_count'] = len(city_regions)
        patterns['city_avg_votes'] = city_regions['得票数'].mean()
    
    if not town_regions.empty:
        patterns['town_total_votes'] = town_regions['得票数'].sum()
        patterns['town_regions_count'] = len(town_regions)
        patterns['town_avg_votes'] = town_regions['得票数'].mean()
    
    return patterns

def generate_team_mirai_report(analysis, patterns, team_mirai_data, merged_data=None, proportional_analysis=None):
    """チームみらい分析レポートを生成"""
    report = []
    report.append("=" * 70)
    report.append("チームみらい（武藤かず子）詳細分析レポート")
    report.append(f"作成日時: {datetime.now()}")
    report.append("=" * 70)
    
    # 基本情報
    report.append("\n【基本選挙結果】")
    report.append(f"候補者名: 武藤　かず子 (チームみらい(新)) - 新人")
    report.append(f"対象市区町村数: {analysis['regions_count']}地域")
    report.append(f"総得票数: {analysis['total_votes']:,}票")
    if 'overall_vote_rate' in analysis:
        report.append(f"全体得票率: {analysis['overall_vote_rate']:.2f}%")
    
    # 統計情報
    report.append("\n【得票数統計情報】")
    report.append(f"平均得票数: {analysis['avg_votes']:.1f}票")
    report.append(f"中央値: {analysis['median_votes']:.1f}票")
    report.append(f"標準偏差: {analysis['std_votes']:.1f}票")
    
    report.append(f"\n最高得票数: {analysis['max_votes_count']:,}票 ({analysis['max_votes_region']})")
    report.append(f"最低得票数: {analysis['min_votes_count']:,}票 ({analysis['min_votes_region']})")
    
    # 得票率分析
    if 'avg_vote_rate' in analysis:
        report.append("\n【得票率統計情報】")
        report.append(f"平均得票率: {analysis['avg_vote_rate']:.2f}%")
        report.append(f"中央値: {analysis['median_vote_rate']:.2f}%")
        report.append(f"標準偏差: {analysis['std_vote_rate']:.2f}%")
        
        report.append(f"\n最高得票率: {analysis['max_rate_value']:.2f}% ({analysis['max_rate_region']}) [有効投票総数: {analysis['max_rate_total_votes']:,}票]")
        report.append(f"最低得票率: {analysis['min_rate_value']:.2f}% ({analysis['min_rate_region']}) [有効投票総数: {analysis['min_rate_total_votes']:,}票]")
    
    # パフォーマンス別地域分析
    if 'high_performance_regions' in analysis:
        report.append("\n【パフォーマンス別地域分析】")
        report.append(f"高パフォーマンス地域 (得票率3.0%以上): {len(analysis['high_performance_regions'])}地域")
        if analysis['high_performance_regions']:
            for region in analysis['high_performance_regions']:
                region_data = merged_data[merged_data['市区町村名'] == region].iloc[0]
                report.append(f"  • {region}: {region_data['得票率']:.2f}% ({region_data['得票数']:,}票)")
        
        report.append(f"\n中パフォーマンス地域 (得票率2.0-3.0%): {len(analysis['medium_performance_regions'])}地域")
        if analysis['medium_performance_regions']:
            # 全ての中パフォーマンス地域を表示
            for region in analysis['medium_performance_regions']:
                region_data = merged_data[merged_data['市区町村名'] == region].iloc[0]
                report.append(f"  • {region}: {region_data['得票率']:.2f}% ({region_data['得票数']:,}票)")
        
        report.append(f"\n基本パフォーマンス地域 (得票率2.0%未満): {len(analysis['low_performance_regions'])}地域")
        if analysis['low_performance_regions']:
            # 全ての基本パフォーマンス地域を表示
            for region in analysis['low_performance_regions']:
                region_data = merged_data[merged_data['市区町村名'] == region].iloc[0]
                report.append(f"  • {region}: {region_data['得票率']:.2f}% ({region_data['得票数']:,}票)")
    
    # 地域パターン分析
    report.append("\n【地域パターン分析】")
    
    # さいたま市分析
    if 'saitama_total_votes' in patterns:
        report.append(f"\nさいたま市内の結果:")
        report.append(f"  対象区数: {patterns['saitama_regions_count']}区")
        report.append(f"  合計得票数: {patterns['saitama_total_votes']:,}票")
        report.append(f"  平均得票数: {patterns['saitama_avg_votes']:.1f}票")
        report.append(f"  全得票数に占める割合: {(patterns['saitama_total_votes'] / analysis['total_votes']) * 100:.1f}%")
        
        report.append(f"\n  さいたま市各区の詳細:")
        for region_info in patterns['saitama_regions']:
            report.append(f"    • {region_info['市区町村名']}: {region_info['得票数']:,}票")
    
    # 市部と町村部の比較
    if 'city_total_votes' in patterns and 'town_total_votes' in patterns:
        report.append(f"\n市部 vs 町村部の比較:")
        report.append(f"  市部: {patterns['city_regions_count']}地域, {patterns['city_total_votes']:,}票 (平均: {patterns['city_avg_votes']:.1f}票)")
        report.append(f"  町村部: {patterns['town_regions_count']}地域, {patterns['town_total_votes']:,}票 (平均: {patterns['town_avg_votes']:.1f}票)")
        
        city_ratio = (patterns['city_total_votes'] / analysis['total_votes']) * 100
        town_ratio = (patterns['town_total_votes'] / analysis['total_votes']) * 100
        report.append(f"  市部得票割合: {city_ratio:.1f}%")
        report.append(f"  町村部得票割合: {town_ratio:.1f}%")
    
    # 全地域ランキング
    if merged_data is not None and '得票率' in merged_data.columns:
        report.append("\n【全地域得票率ランキング】")
        ranking_data = merged_data[['市区町村名', '得票数', '得票率', '有効投票総数']].copy()
        ranking_data = ranking_data.sort_values('得票率', ascending=False)
        
        # 全地域を表示（省略なし）
        for i, (idx, row) in enumerate(ranking_data.iterrows(), 1):
            report.append(f"{i:2d}. {row['市区町村名']}: {row['得票率']:.2f}% ({row['得票数']:,}票) [有効投票総数: {row['有効投票総数']:,}票]")
    
    # 比例分析結果の追加
    if proportional_analysis and proportional_analysis:
        report.append("\n" + "=" * 70)
        report.append("【比例代表選挙での結果】")
        report.append("=" * 70)
        
        report.append(f"\n政党名: チームみらい")
        report.append(f"総得票数: {proportional_analysis['total_votes']:,}票")
        
        if 'overall_rate' in proportional_analysis:
            report.append(f"全体得票率: {proportional_analysis['overall_rate']:.2f}%")
        
        if 'avg_rate' in proportional_analysis:
            report.append(f"平均得票率: {proportional_analysis['avg_rate']:.2f}%")
            report.append(f"中央値得票率: {proportional_analysis['median_rate']:.2f}%")
            report.append(f"標準偏差: {proportional_analysis['std_rate']:.2f}%")
        
        if 'regions_count' in proportional_analysis:
            report.append(f"対象地域数: {proportional_analysis['regions_count']}地域")
        
        # 統計情報
        if 'avg_votes' in proportional_analysis:
            report.append(f"\n【比例代表での得票数統計】")
            report.append(f"平均得票数: {proportional_analysis['avg_votes']:.1f}票")
            report.append(f"中央値: {proportional_analysis['median_votes']:.1f}票")
            report.append(f"標準偏差: {proportional_analysis['std_votes']:.1f}票")
            
            report.append(f"\n最高得票数: {proportional_analysis['max_votes_count']:,}票 ({proportional_analysis['max_votes_region']})")
            report.append(f"最低得票数: {proportional_analysis['min_votes_count']:,}票 ({proportional_analysis['min_votes_region']})")
        
        # 得票率情報
        if 'max_rate_value' in proportional_analysis:
            report.append(f"\n最高得票率: {proportional_analysis['max_rate_value']:.2f}% ({proportional_analysis['max_rate_region']}) [有効投票総数: {proportional_analysis['max_rate_total_votes']:,}票]")
            report.append(f"最低得票率: {proportional_analysis['min_rate_value']:.2f}% ({proportional_analysis['min_rate_region']}) [有効投票総数: {proportional_analysis['min_rate_total_votes']:,}票]")
        
        # 地域別ランキング
        if 'detailed_data' in proportional_analysis:
            detailed_data = proportional_analysis['detailed_data']
            if not detailed_data.empty and '得票率' in detailed_data.columns:
                report.append(f"\n【比例代表での地域別得票率ランキング】")
                detailed_sorted = detailed_data.sort_values('得票率', ascending=False)
                for idx, (_, row) in enumerate(detailed_sorted.iterrows(), 1):
                    valid_votes_col = '有効投票数' if '有効投票数' in detailed_data.columns else '有効投票総数'
                    if valid_votes_col in row:
                        report.append(f"{idx:2d}. {row['市区町村名']}: {row['得票率']:.2f}% ({row['得票数']:,}票) [{valid_votes_col}: {row[valid_votes_col]:,}票]")
                    else:
                        report.append(f"{idx:2d}. {row['市区町村名']}: {row['得票率']:.2f}% ({row['得票数']:,}票)")
            elif not detailed_data.empty:
                # 得票率がない場合は得票数ランキングを表示
                report.append(f"\n【比例代表での地域別得票数ランキング】")
                detailed_sorted = detailed_data.sort_values('得票数', ascending=False)
                for idx, (_, row) in enumerate(detailed_sorted.iterrows(), 1):
                    report.append(f"{idx:2d}. {row['市区町村名']}: {row['得票数']:,}票")
        
        # 選挙区と比例の比較分析
        if 'overall_vote_rate' in analysis and 'overall_rate' in proportional_analysis:
            report.append(f"\n【選挙区 vs 比例代表 比較分析】")
            report.append(f"選挙区での得票率: {analysis['overall_vote_rate']:.2f}%")
            report.append(f"比例代表での得票率: {proportional_analysis['overall_rate']:.2f}%")
            
            # 差の分析
            diff = proportional_analysis['overall_rate'] - analysis['overall_vote_rate']
            if diff > 0:
                report.append(f"比例の方が{diff:.2f}ポイント高い")
            else:
                report.append(f"選挙区の方が{abs(diff):.2f}ポイント高い")
            
            # 得票数の比較
            if 'total_votes' in proportional_analysis:
                prop_votes = proportional_analysis['total_votes']
                district_votes = analysis['total_votes']
                votes_diff = prop_votes - district_votes
                if votes_diff > 0:
                    report.append(f"比例の方が{votes_diff:,}票多い")
                else:
                    report.append(f"選挙区の方が{abs(votes_diff):,}票多い")
                
                # 比率分析
                if district_votes > 0:
                    ratio = prop_votes / district_votes
                    report.append(f"比例得票数は選挙区得票数の{ratio:.2f}倍")
        
        # さいたま市内での比較（比例vs選挙区）
        if 'detailed_data' in proportional_analysis and merged_data is not None:
            report.append(f"\n【さいたま市内での選挙区vs比例比較】")
            saitama_prop = detailed_data[detailed_data['市区町村名'].str.contains('さいたま市', na=False)]
            saitama_district = merged_data[merged_data['市区町村名'].str.contains('さいたま市', na=False)]
            
            if not saitama_prop.empty and not saitama_district.empty:
                prop_saitama_total = saitama_prop['得票数'].sum()
                district_saitama_total = saitama_district['得票数'].sum()
                
                report.append(f"さいたま市内 比例得票数: {prop_saitama_total:,}票")
                report.append(f"さいたま市内 選挙区得票数: {district_saitama_total:,}票")
                
                if district_saitama_total > 0:
                    saitama_ratio = prop_saitama_total / district_saitama_total
                    report.append(f"さいたま市内では比例が選挙区の{saitama_ratio:.2f}倍の得票")
    
    report.append("\n" + "=" * 70)
    report.append("チームみらい詳細分析完了")
    report.append("=" * 70)
    
    return "\n".join(report)

def main():
    """メイン実行関数"""
    print("チームみらい詳細分析を開始します...")
    
    # データ読み込み
    candidate_data = load_candidate_data()
    voting_results = load_voting_results()
    voting_info = load_voting_info()
    proportional_candidate_data, proportional_results_data = load_proportional_data()
    
    if candidate_data is None:
        print("候補者データが読み込めませんでした。処理を終了します。")
        return
    
    # チームみらいデータ抽出
    team_mirai_data = extract_team_mirai_data(candidate_data)
    
    if team_mirai_data.empty:
        print("チームみらいのデータが見つかりませんでした。")
        return
    
    # 分析実行
    analysis, merged_data = analyze_team_mirai_performance(team_mirai_data, voting_results, voting_info)
    patterns = analyze_regional_patterns(team_mirai_data)
    
    # 比例分析実行
    proportional_analysis = analyze_proportional_performance(proportional_candidate_data, proportional_results_data)
    
    # レポート生成
    report = generate_team_mirai_report(analysis, patterns, team_mirai_data, merged_data, proportional_analysis)
    
    # 出力ディレクトリ作成
    os.makedirs('team_mirai_analysis', exist_ok=True)
    
    # レポート保存
    output_file = 'team_mirai_analysis/チームみらい詳細分析レポート_完全版.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"チームみらい詳細分析レポート（完全版）が生成されました: {output_file}")
    
    # 結果を画面にも表示
    print("\n" + report)

if __name__ == "__main__":
    main()
