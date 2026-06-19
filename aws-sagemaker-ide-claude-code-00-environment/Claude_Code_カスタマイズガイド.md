# 🚀 Claude Code カスタマイズガイド

---

## 📌 1. カスタマイズ機能の全体像

### 🔹 5つの機能

| 誰が動くか | いつ読み込まれるか | 機能 |
|---|---|---|
| Claude 本体 | 常時 | CLAUDE.md |
| Claude 本体 | 条件付き | `.claude/rules/` |
| Claude 本体 | 手動（`/コマンド`）または自動（Claude 判断） | Skills |
| 別 Claude | 必要時（Claude が自律起動） | サブエージェント |
| シェル | 自動（決定論的） | Hooks |

> ⚠️ **カスタムコマンドは Skills に統合されました（2025年末〜）**
> `.claude/commands/` は後方互換で動作しますが、新規作成は Skills（`.claude/skills/`）が推奨です。

> - `.claude/rules/`：`paths` フィールドでファイルパターンを指定
> - Skills：説明（description）がメモリに常駐、本文は呼び出し時のみ読み込み
> - Hooks：ライフサイクルイベントで自動実行されるコマンド

---

### 🔹 どの機能をいつ使うべきか（判断フローチャート）

| 判断基準 | 使う機能 |
|---|---|
| Q1：確実に実行したい処理 | **Hooks** |
| Q2：独立コンテキストで作業させたい（重たい処理） | **サブエージェント** |
| Q3：常に適用したい | **CLAUDE.md** |
| Q4：特定条件でだけ適用したい | **`.claude/rules/`** |
| Q5：必要な時だけ読み込む | **Skills** |
| Q6：ワンクリックで実行 | **Skills**（`/コマンド名` で呼び出す） |

> - 常時意識してほしい → CLAUDE.md
> - 特定タスクだけ意識してほしい → Skills

---

### 🔹 ファイル構造の例

**グローバル設定（全プロジェクト共通）**

```
~/
│
├─ .claude.json              # MCP サーバー設定（User/Local スコープ）・OAuth セッション
│
└─ .claude/
    │
    ├─ CLAUDE.md             # グローバル常時読み込み
    ├─ CLAUDE.local.md       # 個人×全プロジェクト設定（gitignore 対象外）
    ├─ settings.json         # グローバル動作設定
    │
    ├─ agents/               # ユーザーレベルのサブエージェント定義
    │   └─ xxxxx.md
    │
    ├─ skills/               # ユーザーレベルのスキル（全プロジェクト共通）
    │   └─ xxxxx/
    │       └─ SKILL.md
    │
    └─ commands/             # ※後方互換（新規作成は skills/ 推奨）
        └─ xxxxx.md
```

**プロジェクト構造**

```
project-root/
│
├─ CLAUDE.md                      # 常時読み込み（プロジェクト共通）
├─ CLAUDE.local.md                # 個人×プロジェクト設定（自動 gitignore）
├─ .mcp.json                      # MCP サーバー設定（プロジェクトスコープ）
│
├─ .claude/
│   │
│   ├─ settings.json              # チーム共有の動作設定（hooks 定義等）
│   ├─ settings.local.json        # 個人設定（自動 gitignore）
│   │
│   ├─ rules/                     # ルール（paths フィールドで動的読み込み）
│   │   └─ xxxxx.md
│   │
│   ├─ agents/                    # サブエージェント定義
│   │   └─ xxxxx.md
│   │
│   ├─ skills/                    # スキル（カスタムコマンドを統合）
│   │   └─ xxxxx/
│   │       └─ SKILL.md
│   │
│   └─ commands/                  # ※後方互換（新規作成は skills/ 推奨）
│       └─ xxxxx.md
│
├─ src/                           # アプリケーションコード
├─ terraform/                     # インフラコード
└─ docs/                          # プロジェクトドキュメント
```

---

### 🔹 公式ドキュメントを確認させる方法

```
https://code.claude.com/docs/ja
```

サブエージェント（組み込みサブエージェント）を使う方法：

- **方法 1：** `@"claude-code-guide(agent)" 「質問～」`
- **方法 2：** `ClaudeCodeの公式ドキュメントを調べて、「質問～」`

> `@` はファイル・リソースをコンテキストに読み込む参照記号

---

## 📌 2. CLAUDE.md ― プロジェクト知識の土台

### 🔹 CLAUDE.md の本質的な役割と仕組み

- プロジェクトのルールと知識を記述するファイル
- 起動時に自動読み込み／セッションをまたいで永続化
- **具体的かつ簡潔に書く（100〜200 行が目安）**
  - 肥大化したら `.claude/rules/` で分割する
  - 禁止事項には必ず代替案をセットで記載する

---

### 🔹 メモリ階層（5段階の優先順位）

| タイプ | 場所 | 書く内容 |
|---|---|---|
| Enterprise | 組織管理フォルダ | 組織共通ルール |
| **Project** ★ | `./CLAUDE.md` | プロジェクト固有設定 |
| **Project rules** ★ | `.claude/rules/*.md` | モジュール化したルール |
| **User** ★ | `~/.claude/CLAUDE.md` | 個人の共通設定 |
| Local | `./CLAUDE.local.md` | 個人×プロジェクト設定 |

> `Local` は自動的に `.gitignore` 対象となる

---

### 🔹 効果的なルールの書き方

**Project（`./CLAUDE.md`）に書く内容**

```
Project
│
├─ 概要               （プロジェクトの目的、主要機能）
├─ 技術スタック       （言語、フレームワーク、ライブラリ）
├─ ディレクトリ構造   （主要フォルダの役割）
├─ コーディング規約   （命名規則、フォーマット）
└─ 開発ワークフロー   （コミット規約、テスト方針）
```

> - 外部ファイルの内容を読み込む場合は `@` を使用
> - シークレット情報は記載しない

**User（`~/.claude/CLAUDE.md`）に書く内容**

```
User
│
├─ 基本方針           （日本語で書く、TDD開発 など）
└─ エラーハンドリング （根本原因を修正、エラーケースもテスト）
```

---

### 🔹 `/init` コマンドによる作成

`CLAUDE.md` を自動生成するコマンド（初回セットアップ時に実行）。

**最低限の準備（プロジェクトルートに用意するファイル）**

```
project-root/
│
├── README.md           ← 概要、技術スタック、主要コマンド
│
├── package.json        ← Node.js の場合
├── requirements.txt    ← Python の場合
├── go.mod              ← Go の場合
├── Gemfile             ← Ruby の場合
├── pom.xml             ← Java (Maven) の場合
├── build.gradle        ← Java (Gradle) の場合
└── .gitignore          ← あると構成を推測しやすい
```

---

## 📌 3. `.claude/rules/` によるルールのモジュール化

### 🔹 CLAUDE.md 肥大化問題の解決策

- 必要な時だけ、必要なルールを読み込む仕組み
- 特定のファイルを操作した時だけルールを読み込む

---

### 🔹 `paths` フィールドによる動的読み込み（ファイル編集時）

ルールファイルの基本形式（**YAML フロントマター ＋ Markdown 本文**）

```yaml
---
paths: src/components/**
---

Markdown本文
```

> `paths` なしの場合、`CLAUDE.md` と同様に常に読み込まれる

---

### 🔹 Glob パターンの書き方（gitignore と同じ記法）

プロジェクトルートからの相対パスで記述する。

| パターン | マッチ対象 |
|---|---|
| `**/*.ts` | 全ディレクトリの TypeScript ファイル |
| `src/**/*` | `src/` 以下の全ファイル |
| `*.md` | ルート直下の Markdown ファイル |

> - `*`：同一ディレクトリ内のファイル名にマッチ
> - `**`：ディレクトリを再帰的にマッチ
> - `{a,b}`：a または b

---

## 📌 4. Skills（旧：カスタムコマンド）

### 🔹 「レシピ本」アナロジーで理解する段階的読み込み

- 必要な時だけ開く、コンテキストを圧迫しない

**段階的開示（Progressive Disclosure）**

| 段階 | 内容 | トークン目安 |
|---|---|---|
| 第 1 段階 | メタデータ（名前・説明） | 約 100 トークン |
| 第 2 段階 | `SKILL.md` | 5,000 トークン未満 |
| 第 3 段階 | サポートファイル | 必要時のみ |

---

### 🔹 ディレクトリ構造（ディレクトリ名がスキル名になる）

```
skills/
├─ xxxxx/
│   └─ SKILL.md   # スキル（name なし：自動呼び出し）
└─ yyyyy/
    └─ SKILL.md   # スキル（name あり：/コマンド）
```

---

### 🔹 `SKILL.md` の基本構造と `description` の書き方

**(1) スキル（name なし：自動呼び出し）**

```yaml
---
description: 何をするスキルで、いつ使うか
---
```

**(2) スキル（name あり：`/コマンド`）**

```yaml
---
name: スキル名
description: 何をするスキルで、いつ使うか
---
```

#### 💡 ⚠️ `description` の書き方【重要】

Claude が自動呼び出しを判断する際に参照される（「いつ、何をするか」を記述）。Skills・サブエージェント共通のルール。

**呼び出されない時の解決策**

1. `PROACTIVELY`、`MUST BE USED` キーワードを使う
2. `when` 句で発動条件を明確にする
   - `when tests fail.`
   - `when code changes are detected.`
   - `when reviewing PRs.`
3. 具体的なキーワードを含める
4. 明示的に呼び出す（名前を直接指定）

---

### 🔹 `reference.md` / `examples.md` / `scripts/` の活用

```
skill-name/
│
├─ SKILL.md          # 概要・ナビゲーション（目次）
├─ reference.md      # 詳細仕様
├─ examples.md       # 使用例
└─ scripts/          # ユーティリティ
```

**`SKILL.md` からの参照方法（マークダウンリンク）**

```markdown
## Reference
詳細は [reference.md](reference.md) を参照。

## Examples
使用例は [examples.md](examples.md) を参照。
```

> `SKILL.md` 自体は軽量に保つこと（500行以内が目安）

---

### 🔹 AI + スクリプトの協調

スキルの中でスクリプトを呼び出すことで、AI とスクリプトを組み合わせる。

| 担当 | 得意な処理 |
|---|---|
| AI | 判断・要約・文書生成 |
| スクリプト | 機械的・決定論的な処理 |

---

## 📌 5. サブエージェント ― 独立コンテキストの活用

### 🔹 メインエージェントとの違い（コンテキスト独立）

- 独立して作業し、結果のサマリーを返す（並列実行可能）
- 大量のファイル操作が必要な場合に有効（コンテキストを圧迫しない）
- 明確な依頼が必要（メインの会話内容は伝わらない）

---

### 🔹 組み込みサブエージェント

> ユーザーが直接呼び出すことはほとんどない

| エージェント | 説明 |
|---|---|
| General-purpose（汎用） | 全ツールにフルアクセスし、探索と変更の両方が必要な複雑なタスク |
| Explore（探索） | 高速・読み取り専用の調査エージェント |
| Plan（計画） | 読み取り専用でプランモードで動作するリサーチエージェント |

---

### 🔹 プラグイン

スキル・フック・サブエージェント・MCP サーバーを 1 つのインストール可能なユニットとしてまとめたもの。

| プラグイン名 | 説明 |
|---|---|
| `feature-dev` | 3 つの専門エージェントを起動（`code-explorer`、`code-architect`、`code-reviewer`） |
| `code-review` | 5 つの並列 Sonnet エージェントがそれぞれを担当（CLAUDE.md 準拠、バグ検出、変更履歴、PR 履歴、コードコメント） |
| `commit-commands` | git コミットメッセージの自動生成・規約適用 |
| `security-guidance` | Semgrep を使ってセキュリティ脆弱性をリアルタイムで検出 |
| `frontend-design` | フロントエンド UI の構築依頼をするだけでスキルが自動起動 |

---

### 🔹 YAML フロントマター（`name`、`description`、`tools` 等）

```yaml
---
name: code-reviewer
description: コードレビューを行う
model: sonnet
tools: [Read, Grep, Glob, Bash]
disallowedTools: [Write, Edit]
skills:
  - api-conventions
  - error-handling-patterns
mcpServers: [github]
---

本文
```

> `description` の書き方はセクション4「Skills」の【重要】を参照

---

### 🔹 `/agents` コマンドによる作成

`/agents` → **Create new agent** で対話形式で作成できる。

---

### 🔹 Skills とサブエージェントの連携パターン

- Skills（`/コマンド名`）から複数のサブエージェントを**並列**で呼び出す

---

## 📌 6. Hooks ― 決定論的な自動化

### 🔹 確率論的（CLAUDE.md）vs 決定論的（Hooks）の違い

**用途：** 自動フォーマット、通知、検証、ログ、カスタム権限

---

### 🔹 10 種類のフックイベント

**主要イベント**

| イベント | タイミング | 主な用途 |
|---|---|---|
| `PreToolUse` | ツール実行前 | 危険操作をブロック |
| `PostToolUse` | ツール実行後 | 自動フォーマット |
| `Stop` | タスク完了時 | 完了通知 |
| `SessionStart` | 起動時 | 環境の初期化 |

**低頻度イベント**

| イベント | タイミング |
|---|---|
| `PermissionRequest` | 権限確認ダイアログ表示時 |
| `Notification` | 通知送信時 |
| `UserPromptSubmit` | プロンプト送信時 |
| `SubagentStop` | サブエージェント完了時 |
| `PreCompact` | コンパクト実行前 |
| `SessionEnd` | セッション終了時 |

---

### 🔹 `settings.json` での設定方法

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "実行するコマンド"
          }
        ]
      }
    ]
  }
}
```

---

### 🔹 マッチャーの基本パターン（`PreToolUse`、`PostToolUse` のみ使用）

どのツールで発火するかを指定する。

| パターン | マッチ対象 |
|---|---|
| `""` または `"*"` | すべてのツール |
| `"Bash"` | Bash ツールのみ |
| `"Write\|Edit"` | Write または Edit |

---

## 📌 7. 補足説明

### 🔹 サブエージェント vs スキル

**サブエージェントが適しているタスク**

- コードレビュー（PR 前）
- バグ調査・デバッグ
- コードの重複検出・整理提案
- リファクタリング提案
- ユニットテスト生成
- E2E テスト設計
- パフォーマンス分析
- セキュリティ脆弱性スキャン
- 依存パッケージの脆弱性チェック
- 大規模ドキュメント生成

**スキルが適しているタスク**

- ドキュメント規約の適用
- コーディング規約の自動適用
- 関数・変数の命名チェック
- コードの簡略化・整形
- インラインコメント追加
- 型定義の補完（TypeScript 等）
- Terraform / CloudFormation の lint チェック
- ソフトウェアの変更履歴の更新
- エラーメッセージの多言語化
- コミットメッセージ生成

---

### 🔹 エージェントチーム

専門特化したエージェントに分割して並列・逐次処理させる。

**処理パターン：** Sequential（逐次）、Parallel（並列）、Hierarchical（階層）

| 例 | エージェント構成 |
|---|---|
| **Spec-Driven Development** | 要件 → 設計 → 実装 → テスト |
| **インフラ構築・変更管理** | 調査 → 設計 → レビュー → 適用 |
| **障害対応・インシデント管理** | 検知 → 原因特定 → 対応 → 報告 |
| **セキュリティ監査** | 収集 → 診断 → 評価 → 改善提案 |
| **ドキュメント自動生成** | 読取 → 構造化 → 執筆 → 校正 |
| **コスト最適化分析** | データ収集 → 分析 → 提案 → 試算 |
| **CI/CD パイプライン設計** | 要件ヒアリング → 設計 → 実装 → 検証 |

---

### 🔹 MCP（Model Context Protocol）

| No. | MCP 名 | 用途 |
|---|---|---|
| 01 | GitHub MCP | コード管理の自動化 |
| 02 | GitLab MCP | オンプレ MR・パイプライン管理 |
| 03 | AWS MCP | インフラ調査・分析 |
| 04 | Azure MCP | リソースグループ・コスト・AKS の参照 |
| 05 | GCP MCP | BigQuery・GCS・Cloud Run の操作・参照 |
| 06 | Datadog MCP | メトリクス取得・アラート確認・ダッシュボード参照 |
| 07 | Elasticsearch MCP | ログ検索・インデックス管理・障害調査 |
| 08 | PagerDuty MCP | インシデント検知・エスカレーション・対応記録 |
| 09 | Playwright MCP | E2E テストの自動生成・実行・結果分析 |
| 10 | Figma MCP | デザインデータの参照・実装との整合性確認 |
| 11 | Notion MCP | 設計メモ・ナレッジベースの管理・更新 |
| 12 | Redmine MCP | チケット管理の自動化 |

---

### 🔹 スラッシュコマンド一覧

| コマンド | 説明 |
|---|---|
| `/clear` | 会話履歴・コンテキストをリセット |
| `/init` | `CLAUDE.md` を自動生成（初回セットアップ） |
| `/compact` | コンテキストを要約して圧縮（トークン節約） |
| `/memory` | `CLAUDE.md` の内容を確認・編集 |
| `/model` | 使用モデルを切り替え（Sonnet ↔ Opus など） |
| `/agents` | サブエージェントを作成・管理 |
| `/bug` | GitHub にバグ報告を開く |
| `/doctor` | Claude Code の設定・環境の診断 |
| `/config` | 設定確認 |
| `/help` | 使えるコマンド一覧を表示 |

---

### 🔹 権限モード（`SHIFT+TAB` で切り替え）

| モード | 動作 |
|---|---|
| `default` | 標準動作。各ツールの最初の使用時に権限を確認 |
| `acceptEdits` | セッション中のファイル編集権限を自動的に受け入れ |
| `plan` | ファイルの変更・コマンド実行ができない（計画のみ） |
| `auto` | 危険なコマンドと判断されない限り、自動的に受け入れ |
| `dontAsk` | ルールで事前承認されていない場合、自動的に拒否 |
| `bypassPermissions` | 全ての権限プロンプトをスキップ |

```bash
# bypassPermissions の使用方法
claude --dangerously-skip-permission
```

---

### 🔹 `settings.json` での権限制御

| 設定 | 動作 |
|---|---|
| `allow` | 確認なしで自動許可 |
| `deny` | 即時ブロック |
| `PreToolUse Hook` | 実行前にスクリプトで追加チェック |

> 優先順位：`deny` > `allow` > Default（都度確認）
