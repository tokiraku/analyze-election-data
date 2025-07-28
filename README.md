# 埼玉県選挙結果分析プロジェクト

## 📊 プロジェクト概要
埼玉県の選挙結果データを包括的に分析するプロジェクトです。
選挙区・比例代表の両方のデータを汎用的に処理し、特にチームみらいの選挙結果を詳細に分析して地域別の支持動向を可視化します。

---

# 🚀 環境セットアップ

## 仮想環境の作成
下記のコマンドを実行して、仮想環境を作成します。

```bash
python -m venv env
```

## 仮想環境の有効化

**Windowsの場合:**
```bash
.\env\Scripts\activate
```

**LinuxやMacの場合:**
```bash
source env/bin/activate
```

## 必要なパッケージのインストール
次に、必要なパッケージをインストールします。以下のコマンドを実行してください。

```bash
pip install -r requirements.txt
```

## 仮想環境の終了
仮想環境を終了するには、以下のコマンドを実行します。

```bash
deactivate
```

---

# 📈 データ処理・分析システム

## 🔄 データ処理パイプライン

### ステップ1: 選挙区データの処理
```bash
python cleanup_voting_result_by_electoral_district.py
```

**実行内容:**
- 選挙区投票結果の包括的データクリーンアップ
- 候補者別市区町村別得票データを縦並び形式に変換
- 重複除去・データ整合性チェック・欠損値補完

**出力ディレクトリ:** `output/`
- `候補者別市区町村別得票調べ_縦並び版.csv`
- その他の選挙区関連データファイル

### ステップ2: 比例代表データの処理（汎用システム）
```bash
python cleanup_voting_result_by_proportional_representation.py
```

**実行内容:**
- **汎用的Excel直接抽出システム**による全政党・全地区対応
- 16政党×72開票区の完全データセット生成（1152件）
- 不足データの自動検出・補完（ハードコーディング不使用）
- 政党ヘッダー行の動的検出・数値パターン分析による補完

**出力ディレクトリ:** `output_proportional/`
- `比例代表_得票総数の開票区別政党等別一覧_縦並び版.csv` - **全16政党完全データ**
- `比例代表_名簿登載者の得票総数の政党別一覧_縦並び版.csv` - 候補者別データ  
- `比例代表_開票結果調べ_縦並び版.csv` - 開票結果詳細
- `比例代表_処理サマリーレポート.txt` - 処理結果概要

**バックアップ:** `tmp_proportional/` - 処理前データ保存

### ステップ3: 投票情報データの処理
```bash
# 選挙区投票情報
python cleanup_voting_info_by_electoral_district.py

# 比例代表投票情報  
python cleanup_voting_info_by_proportional_representation.py
```

**出力ディレクトリ:** `output_info/`, `output_info_proportional/`

### ステップ4: 詳細分析実行
```bash
python team_mirai_detailed_analysis.py
```

**実行内容:**
- チームみらいの包括的分析実行
- 選挙区・比例代表の詳細統計分析
- 地域別ランキング・得票率計算

### ステップ5: サポーター・演説街宣効果分析（新機能）
```bash
python supporter_campaign_analysis.py
```

**実行内容:**
- サポーター数と得票数・得票率の相関分析
- 演説・街宣活動の効果分析
- 総投票数規模別の演説街宣効果比較
- 相関係数・統計的効果測定

**出力ディレクトリ:** `supporter_campaign_analysis/`
- `サポーター演説街宣分析_詳細データ.csv` - 全データ統合ファイル
- `サポーター演説街宣分析_レポート.txt` - 詳細分析レポート

## 🎯 実行方法（用途別）

### 📋 全データ処理実行（推奨）
```bash
cd C:\Users\redcr\OneDrive\ドキュメント\GitHub\analyze_voting

# 全データ処理パイプライン実行
python cleanup_voting_result_by_electoral_district.py
python cleanup_voting_result_by_proportional_representation.py
python cleanup_voting_info_by_electoral_district.py  
python cleanup_voting_info_by_proportional_representation.py
python team_mirai_detailed_analysis.py
python supporter_campaign_analysis.py
```

または、PowerShellで連続実行:
```powershell
cd "C:\Users\redcr\OneDrive\ドキュメント\GitHub\analyze_voting"
python cleanup_voting_result_by_electoral_district.py; python cleanup_voting_result_by_proportional_representation.py; python team_mirai_detailed_analysis.py; python supporter_campaign_analysis.py
```

### 🔄 比例代表のみ再処理
```bash
python cleanup_voting_result_by_proportional_representation.py
```

### 📊 分析のみ実行（データ処理済みの場合）
```bash
python team_mirai_detailed_analysis.py
```

## 📁 出力ファイル構成

### 📊 **output/** ディレクトリ（選挙区処理済み）
- `候補者別市区町村別得票調べ_縦並び版.csv` - 選挙区全候補者データ
- その他選挙区関連の処理済みCSVファイル

### 🗳️ **output_proportional/** ディレクトリ（比例代表処理済み）
- `比例代表_得票総数の開票区別政党等別一覧_縦並び版.csv` - **全16政党×72地区完全データ（1152件）**
- `比例代表_名簿登載者の得票総数の政党別一覧_縦並び版.csv` - 候補者別データ  
- `比例代表_開票結果調べ_縦並び版.csv` - 開票結果詳細
- `比例代表_処理サマリーレポート.txt` - 処理結果概要

### 📈 **output_info/** / **output_info_proportional/** ディレクトリ
- 投票情報（投票率・投票者数等）の処理済みデータ

### 🏆 **team_mirai_analysis/** ディレクトリ
- `チームみらい詳細分析レポート_完全版.txt` - **メインレポート**（推奨読み物）

### 📋 **external_data/** ディレクトリ
- `武藤さん演説・街宣.csv` - 選挙活動スケジュールデータ
- `サポーター.csv` - サポーター関連データ

### 💾 **tmp_*** ディレクトリ群
- `tmp/`, `tmp_proportional/`, `tmp_info/`, `tmp_info_proportional/` - 各処理の中間・バックアップデータ

## 🚀 新機能・改良点

### 🔧 汎用的Excel直接抽出システム
- **ハードコーディング不使用**: 特定の地区・政党に依存しない汎用設計
- **動的ヘッダー検出**: 政党名の配置を自動検出（15個のヘッダー行を発見）
- **全地区対応**: 72地区を自動識別・処理
- **数値パターン分析**: 得票数の数値パターンから不足データを自動補完
- **完全データセット**: 16政党×72地区=1152件の完全なデータを生成

### 📊 改良された分析機能
- 不完全な地区の自動検出・補正
- Excel原本からの直接データ抽出
- 重複除去・データ整合性の自動チェック

## ⚠️ トラブルシューティング

### エラー: ファイルが見つからない
```
❌ データファイルが見つかりません
```
**解決方法:** データ処理を実行してください
```bash
python cleanup_voting_result_by_electoral_district.py
python cleanup_voting_result_by_proportional_representation.py
```

### エラー: pandas が見つからない
```
ModuleNotFoundError: No module named 'pandas'
```
**解決方法:** 必要なライブラリをインストールしてください
```bash
pip install -r requirements.txt
```

### エラー: 元データファイルが見つからない
```
❌ 埼玉投票結果_比例代表.xls が見つかりません
```
**解決方法:** 以下のファイルがプロジェクトルートに存在することを確認
- `埼玉投票結果_選挙区.xls`
- `埼玉投票結果_比例代表.xls`
- `埼玉投票情報_選挙区.xls`
- `埼玉投票情報_比例代表.xls`

### エラー: xlrd エンジンエラー
```
❌ xlrd engine does not support .xlsx files
```
**解決方法:** xlrdライブラリが正しくインストールされていることを確認
```bash
pip install xlrd==2.0.1
```

## 📈 主要な分析結果

### 選挙区（武藤かず子）
- **総得票数**: 213,087票
- **選挙区総投票数**: 6,830,650票
- **平均得票率**: 2.70%
- **対象地域**: 144市区町村
- **最高得票率**: 蕨市（6.61%、2,314票）
- **最多得票数**: 川口市（13,043票、4.97%）

### 比例代表（チームみらい）
- **総得票数**: 89,049票
- **比例代表総投票数**: 2,911,436票
- **平均得票率**: 2.52%
- **対象地域**: 72開票区
- **候補者数**: 3名
  - 安野たかひろ: 13,327票（95.1%）
  - 高山さとし: 429票（3.1%）
  - 須田えいたろう: 264票（1.9%）

### 📊 データ処理実績（2025/07/22更新）
- **選挙区データ**: 144地域の完全処理
- **比例代表データ**: 16政党×72地区=1152件の完全データセット
- **汎用抽出成功**: さいたま市西区等の不完全地区を自動補正
- **データ品質**: 重複除去・欠損値補完・整合性チェック完了

## 🎯 分析のポイント

1. **地域特性**: 都市部・住宅地での支持が厚く、農村部・山間部で支持が薄い
2. **個人 vs 政党**: 選挙区（個人支持2.70%）が比例代表（政党支持2.52%）をやや上回る
3. **支持基盤**: 蕨市、戸田市、川口市、さいたま市各区で強い支持
4. **新党実績**: 新党として一定の支持基盤を確立
5. **総投票数分析**: 各地域の総投票数と得票数の関係性を詳細分析
6. **データ完全性**: 汎用的Excel抽出により全政党・全地区の正確なデータを確保

## 🔧 技術的特徴

### 汎用的データ処理システム
- **Excel直接読み込み**: xlrdエンジンによる.xlsファイル直接処理
- **動的構造解析**: 政党ヘッダー・地区データの自動検出
- **ハードコーディング不使用**: 特定値に依存しない拡張可能な設計
- **データ品質保証**: 重複除去・欠損値補完・整合性チェック

### 対応データ形式
- **比例代表**: 16政党（日本共産党、日本維新の会、無所属連合、日本保守党、立憲民主党、参政党、国民民主党、チームみらい、日本誠真会、社会民主党、れいわ新選組、日本改革党、自由民主党、再生の道、公明党、ＮＨＫ党）
- **選挙区**: 全候補者対応
- **地域**: 埼玉県全72開票区・144市区町村

## 🔧 システム要件
- **OS**: Windows (PowerShell対応)
- **Python**: 3.7以上
- **ライブラリ**: pandas, xlrd
- **データ**: 処理対象の選挙データファイル（output/, output_proportional/ ディレクトリ）

## 📝 更新履歴
- **2025/07/22**: 汎用的Excel直接抽出システム実装
  - ハードコーディング依存を完全除去
  - 動的政党ヘッダー検出（15個のセクション自動識別）
  - 全72地区・16政党の完全データセット生成（1152件）
  - さいたま市西区等の不完全地区を自動補正
- **2025/07/21**: 総投票数列を追加し、詳細な得票率分析を実現
- **2025/07/21**: 重複ファイルを整理し、統合分析プログラムに集約
- 複数の個別プログラムから核心プログラムに統合
- 不要な重複レポートファイルを削除し、メインレポートに集約
- 全処理実行方法をREADMEに詳細記載
- external_dataディレクトリ追加（選挙活動データ等）

## 🎬 プロジェクト構成

```
analyze_voting/
├── 📊 データ処理スクリプト
│   ├── cleanup_voting_result_by_electoral_district.py      # 選挙区データ処理
│   ├── cleanup_voting_result_by_proportional_representation.py  # 比例代表データ処理（汎用システム）
│   ├── cleanup_voting_info_by_electoral_district.py        # 選挙区投票情報処理
│   ├── cleanup_voting_info_by_proportional_representation.py   # 比例代表投票情報処理
│   ├── team_mirai_detailed_analysis.py                     # チームみらい詳細分析
│   └── detailed_comparison_analysis_csv.py                 # 比較分析
├── 🗃️ 元データファイル
│   ├── 埼玉投票結果_選挙区.xls
│   ├── 埼玉投票結果_比例代表.xls
│   ├── 埼玉投票情報_選挙区.xls
│   └── 埼玉投票情報_比例代表.xls
├── 📁 出力ディレクトリ
│   ├── output/                    # 選挙区処理済みデータ
│   ├── output_proportional/       # 比例代表処理済みデータ（1152件完全セット）
│   ├── output_info/              # 選挙区投票情報
│   ├── output_info_proportional/ # 比例代表投票情報
│   └── team_mirai_analysis/      # チームみらい分析結果
├── 🔄 中間・バックアップデータ
│   ├── tmp/                      # 選挙区中間データ
│   ├── tmp_proportional/         # 比例代表バックアップ
│   ├── tmp_info/                 # 選挙区投票情報中間データ
│   └── tmp_info_proportional/    # 比例代表投票情報中間データ
├── 📈 外部データ
│   └── external_data/
│       ├── 武藤さん演説・街宣.csv    # 選挙活動スケジュール
│       └── サポーター.csv            # サポーター情報
└── 📚 分析結果・比較データ
    └── comparison_analysis/        # 詳細比較分析結果
```

---

# 📚 参考データ
- https://www.pref.saitama.lg.jp/e1701/27san-sokuhou.html
  - 投票情報
    - 埼玉県投票情報_選挙区.xls
    - 埼玉県投票情報_比例代表.xls
  - 投票結果
    - 埼玉県投票結果_選挙区.xls
    - 埼玉県投票結果_比例代表.xls