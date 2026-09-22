# EXP-20260922-50: Order BookとPipe19を比較候補へ追加

状態: Approved / 評価完了（両方とも比較相手として保持、全面ベース不採用）
最終更新: 2026-09-22
関連: EXP-20260922-44、EXP-20260922-48、EXP-20260922-49

## 目的

ユーザー指定の次の公開ノートを静的に取り込み、現在の提出候補v25と既知の強敵に対する価値を調べる。

1. `shiiin9/your-market-list-is-an-order-book`
2. `nathanjacob/kaggriculture-pipe19-sale-advance-overflow`

Kaggleへの提出は行わない。

## 方法

- Kaggle公式CLIでnotebookとmetadataを取得する。
- 公開セルは実行せず、ASTで文字列リテラルとして埋め込まれた提出コードだけを抽出する。
- SHA-256、ライセンス、外部I/O、最後のcallable、壊れた観測、推論時間を確認する。
- 安全にローカル実行できるものだけを、v25・v22・JAXA・v49・pipe18等へCPU逐次評価する。
- runnerと独立watcherで完了を監視し、各段階の終了後すぐ次へ進む。

## 結果

### 静的確認とpreflight

| 項目 | Order Book | Pipe19 |
|---|---:|---:|
| サイズ | 1,026,965 bytes | 1,035,995 bytes |
| SHA-256 | `a16e0e9b...d84d82ab` | `111863bd...48b1c51` |
| 系統 | V55 + Order Book + tomato gate + 4定数 | Pipe18 + ADV + R148 |
| 正常720 step | 完走 | 完走 |
| 中央値 / p99 / 最悪 | 0.89 / 6.12 / 62.13ms | 0.89 / 6.47 / 111.97ms |
| 壊れた観測 | `KeyError('step')`、3項目不合格 | `KeyError('step')`、3項目不合格 |

両notebookの `EXPECTED_SHA256` と抽出ファイルは一致した。抽出器は
`EXPECTED_MAIN_SHA256` だけを自動認識するため表示上は「期待値なし」だった。ライセンスは双方
Apache-2.0。Order Bookの `open(path)` は `path=None` に固定され無効。Pipe19は環境変数
`V92_SELL_LIB` 指定時だけ外部ファイルを読む任意経路があるため、評価時は設定していない。

### 作者の主張（未検証情報として取り扱い）

- Order Book: V55から7公開相手への280戦を191-53から280-0へ改善、平均+758円。Layer D、
  トマト収益ゲート、4定数変更の合成結果。
- Pipe19: 14相手で88.3%、V56へ90%。Pipe18比で+4.2 percentage points。

### 手元パネル

runnerは11セットを完走し、独立watcherも `complete` を確認した。全セットで例外0件。

| 対戦（左側視点） | 勝敗 | 平均差±標準誤差 | 左側の家畜逃走 |
|---|---:|---:|---:|
| Order Book vs v25 | 3-7 | -122.5±379.4円 | 0 |
| Pipe19 vs v25 | 6-4 | +213.8±339.5円 | 0 |
| Order Book vs Pipe19 | 5-5 | -349.7±261.2円 | 0 |
| Pipe19 vs Pipe18 | 8-2 | +704.0±231.0円 | 0 |
| Order Book vs V56 | 4-1 | +651.2±494.0円 | 0 |
| Order Book vs JAXA | 0-5 | -16,862.8±2,043.6円 | 1 |
| Pipe19 vs JAXA | 0-5 | -13,066.4±2,450.9円 | 1 |
| Order Book vs v49 | 2-3 | +502.4±1,392.8円 | 0 |
| Pipe19 vs v49 | 3-2 | +759.8±454.1円 | 0 |
| Order Book vs More Wheat | 5-0 | +249.0±58.4円 | 0 |
| Pipe19 vs More Wheat | 5-0 | +991.0±296.3円 | 0 |

Order BookはV56・More Wheatへ強いが、v25へ3-7、JAXAへ0-5でV55系の異系統弱点を継承した。
Pipe19のADV/R148はPipe18へ8-2・+704円なので同系統内の追加層として明確に有効。v49もPipe18の
2-3・-244円からPipe19は3-2・+760円へ改善した。しかしJAXAへは0-5のままで、家畜逃走も残る。

## 判断

- 両方とも全面ベースにはしない。壊れた観測への安全性未達とJAXA 0-5が決定的。
- v25を提出候補として維持する。Order Book対v25は差が標準誤差より小さく、Pipe19対v25も同様に
  明確な全面優位ではない。
- 部分移植候補としては、Order Book全体よりPipe19の **R148単体** を先に検討する。overflowで
  失われる在庫だけを売るなら影響範囲が狭い。次にOrder BookのLayer D単体、最後にmirror依存の
  ADVを評価する。
- Order BookとPipe19は新しい強敵回帰相手として保持する。Kaggleへの提出は行っていない。
