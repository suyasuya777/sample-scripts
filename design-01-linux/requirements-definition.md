# 📘 Linux サーバー構築 要件定義書

## 🔷 改訂履歴

| 版数 | 改訂日 | 改訂者 | 改訂内容 |
|------|--------|--------|----------|
| 1.0 | 2025-06-17 | 作成者 | 初版作成 |

---

## 📋 目次

- [📘 Linux サーバー構築 要件定義書](#-linux-サーバー構築-要件定義書)
  - [🔷 改訂履歴](#-改訂履歴)
  - [📋 目次](#-目次)
  - [🔷 1. 目的・背景](#-1-目的背景)
  - [🔷 2. 対象範囲（スコープ）](#-2-対象範囲スコープ)
  - [🔷 3. 機能要件](#-3-機能要件)
    - [▶️ 3.1 Linux本体・OS基本設定](#️-31-linux本体os基本設定)
    - [▶️ 3.2 ストレージ・ファイルシステム](#️-32-ストレージファイルシステム)
    - [▶️ 3.3 ネットワーク](#️-33-ネットワーク)
    - [▶️ 3.4 ユーザー・認証管理](#️-34-ユーザー認証管理)
    - [▶️ 3.5 セキュリティ](#️-35-セキュリティ)
    - [▶️ 3.6 主要サービス](#️-36-主要サービス)
    - [▶️ 3.7 監査（auditd）](#️-37-監査auditd)
    - [▶️ 3.8 バックアップ](#️-38-バックアップ)
    - [▶️ 3.9 ログ転送・SIEM連携](#️-39-ログ転送siem連携)
    - [▶️ 3.10 EDR・マルウェア対策](#️-310-edrマルウェア対策)
    - [▶️ 3.11 監視](#️-311-監視)
    - [▶️ 3.12 パッチ管理](#️-312-パッチ管理)
    - [▶️ 3.13 sudo・権限管理](#️-313-sudo権限管理)
    - [▶️ 3.14 サービス自動復旧](#️-314-サービス自動復旧)
    - [▶️ 3.15 運用管理サービス](#️-315-運用管理サービス)
  - [🔷 4. 非機能要件](#-4-非機能要件)
  - [🔷 5. 制約事項・前提条件](#-5-制約事項前提条件)


---


## 🔷 1. 目的・背景

本書は、Linux サーバーの新規構築またはリプレイスにあたり、システムに求める要件を定義するものである。  
本定義に基づき基本設計・詳細設計・パラメータリストを策定する。

**前提OS：AlmaLinux 9.4 / RHEL 9.4**（カーネル 5.14.0 系、glibc 2.34）

---

## 🔷 2. 対象範囲（スコープ）

| 分類 | 対象サービス・コンポーネント | 採用バージョン（RHEL9系） | 備考 |
|------|---------------------------|------------------------|------|
| Linux本体 | OS基本設定、カーネル設定、ブートローダー（GRUB2）、systemd | kernel 5.14.0 / systemd 252 | AlmaLinux 9.4 / RHEL 9.4 |
| ストレージ | パーティション設計、ファイルシステム、スワップ | XFS（デフォルト）/ ext4 | LVM2 使用可 |
| ネットワーク | NIC設定、ルーティング、ホスト名・DNS解決 | NetworkManager 1.42 / nmcli | ifcfg形式は廃止方向（keyfile形式推奨） |
| ユーザー管理 | ローカルユーザー、グループ、PAM認証 | PAM 1.5.1 / shadow-utils 4.9 | pam_faillock（pam_tally2廃止） |
| パッケージ管理 | dnf（RHEL9系標準） | DNF 4.14 | yumコマンドはdnfへのエイリアス |
| ログ管理 | rsyslog、systemd-journald | rsyslog 8.2102 / journald（systemd 252） | journald が一次ログ |
| セキュリティ | SELinux、firewalld、nftables、SSH強化 | SELinux 3.5 / firewalld 1.2 / OpenSSH 8.7 | iptablesはnftablesバックエンドに移行 |
| DNS | BIND（named） | BIND 9.16 | DNSSEC対応 |
| Webサーバー | Apache httpd / Nginx | httpd 2.4.57 / Nginx 1.22 | TLS 1.3対応 |
| プロキシ | Squid | Squid 5.5 | |
| ファイル共有 | Samba / NFS | Samba 4.17 / NFS v4.2 | SMB3.1.1対応 |
| メールサービス | Postfix / Dovecot | Postfix 3.5.9 / Dovecot 2.3.16 | |
| DHCPサービス | dhcp-server（ISC DHCP） | ISC DHCP 4.4.2 | KEA DHCPへ移行も検討 |
| LDAP / ディレクトリ | FreeIPA / 389-ds | FreeIPA 4.10 / 389-ds 2.3 | **OpenLDAPはRHEL9で非対応。FreeIPAまたは389-dsを使用** |
| FTPサービス | vsftpd | vsftpd 3.0.5 | FTPS（TLS必須） |
| VPN | OpenVPN | OpenVPN 2.5.9 | WireGuardも選択肢 |
| パケットフィルター | firewalld / nftables | firewalld 1.2 / nftables 1.0.4 | **iptablesはnftablesへの移行期** |
| 監視・IDS | AIDE / Fail2ban | AIDE 0.16 / Fail2ban 1.0 | |
| 時刻同期 | chrony | chrony 4.3 | ntpdは廃止済み |
| ジョブスケジューラー | cron / systemd timer | cronie 1.5.7 / systemd timer | systemd timerを優先推奨 |
| 暗号化 | GPG / LUKS2 | GnuPG 2.3.3 / cryptsetup 2.4 | LUKS1→LUKS2に移行推奨 |

---

## 🔷 3. 機能要件

### ▶️ 3.1 Linux本体・OS基本設定

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-OS-001 | OSインストール後、最小構成でセキュアなベースシステムを構築すること | 必須 |
| FR-OS-002 | ブートローダー（GRUB2 + BLS形式）を正しく設定し、カーネル起動オプションを管理すること | 必須 |
| FR-OS-003 | systemd により必要なサービスのみ自動起動すること | 必須 |
| FR-OS-004 | ホスト名・タイムゾーン・ロケール・キーボードレイアウトを適切に設定すること | 必須 |
| FR-OS-005 | カーネルパラメーター（sysctl）をセキュリティ・パフォーマンス要件に応じて最適化すること | 必須 |
| FR-OS-006 | 共有ライブラリのパスが正しく設定されていること（ldconfig） | 必須 |
| FR-OS-007 | RHEL9系ではdnfによるパッケージ管理を行うこと（yumコマンドはdnfエイリアス） | 必須 |

### ▶️ 3.2 ストレージ・ファイルシステム

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-FS-001 | 用途に応じたパーティション設計（/, /boot, /var, /home, swap等）を実施すること | 必須 |
| FR-FS-002 | 本番環境ではXFS（デフォルト）を使用すること | 必須 |
| FR-FS-003 | スワップ領域を適切なサイズで設定すること（zram使用も選択肢） | 必須 |
| FR-FS-004 | /etc/fstab を UUID ベースで記述すること | 必須 |
| FR-FS-005 | ディスク暗号化はLUKS2形式を使用すること（LUKS1は非推奨） | 推奨 |

### ▶️ 3.3 ネットワーク

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-NW-001 | 固定IPアドレスを設定し、NetworkManager（nmcli）でNIC設定を管理すること | 必須 |
| FR-NW-002 | NIC接続設定はkeyfile形式（/etc/NetworkManager/system-connections/）で管理すること | 必須 |
| FR-NW-003 | DNSクライアント設定（/etc/resolv.conf）を正しく設定すること | 必須 |
| FR-NW-004 | /etc/hosts による名前解決を適切に設定すること | 必須 |

### ▶️ 3.4 ユーザー・認証管理

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-US-001 | rootの直接SSHログインを禁止し、一般ユーザー経由で sudo を使用すること | 必須 |
| FR-US-002 | パスワードポリシー（最小文字数、複雑度、有効期限）をpwqualityで設定すること | 必須 |
| FR-US-003 | PAM pam_faillock によりアカウントロック機能を設定すること（pam_tally2は廃止済み） | 必須 |
| FR-US-004 | FreeIPA / SSSD による集中認証に対応すること（OpenLDAPはRHEL9非対応） | 推奨 |

### ▶️ 3.5 セキュリティ

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-SEC-001 | SELinux を enforcing モードで運用すること | 必須 |
| FR-SEC-002 | firewalld（nftablesバックエンド）により不要なポートをブロックすること | 必須 |
| FR-SEC-003 | OpenSSH 8.7以降を前提にSSH設定を行うこと（廃止パラメーターを使用しないこと） | 必須 |
| FR-SEC-004 | AIDE によりファイル整合性監視を実施すること | 推奨 |
| FR-SEC-005 | Fail2ban によりブルートフォース攻撃対策を実施すること | 推奨 |
| FR-SEC-006 | ディスク暗号化はLUKS2、ファイル暗号化はGPG 2.3以降を使用すること | 推奨 |

### ▶️ 3.6 主要サービス

| 要件ID | サービス | バージョン（RHEL9） | 要件内容 | 優先度 |
|--------|---------|------------------|---------|--------|
| FR-SVC-001 | DNS（BIND） | BIND 9.16 | 権威DNSまたはキャッシュDNSとして動作しゾーン管理を行うこと | 必須 |
| FR-SVC-002 | Apache / Nginx | httpd 2.4.57 / Nginx 1.22 | HTTP/HTTPSのWebサービスを提供すること（TLS 1.3対応） | 必須 |
| FR-SVC-003 | Squid | Squid 5.5 | プロキシサービスを提供しURLフィルタリングを実施すること | 推奨 |
| FR-SVC-004 | Samba | Samba 4.17 | SMB 3.1.1によるWindowsファイル共有を提供すること | 推奨 |
| FR-SVC-005 | NFS | NFS v4.2 | NFSv4.2によるUnix/Linuxファイル共有を提供すること | 推奨 |
| FR-SVC-006 | Postfix | Postfix 3.5.9 | SMTPメール転送エージェントとして動作すること | 必須 |
| FR-SVC-007 | Dovecot | Dovecot 2.3.16 | POP3S/IMAPSによるメール受信サービスを提供すること | 推奨 |
| FR-SVC-008 | DHCP | ISC DHCP 4.4.2 | ネットワーク機器へIPアドレスを動的配布すること | 推奨 |
| FR-SVC-009 | FreeIPA / 389-ds | FreeIPA 4.10 / 389-ds 2.3 | LDAPディレクトリサービスを提供すること（OpenLDAPはRHEL9非対応） | 推奨 |
| FR-SVC-010 | vsftpd | vsftpd 3.0.5 | FTPサービスを提供すること（FTPS/TLS必須） | 推奨 |
| FR-SVC-011 | OpenVPN | OpenVPN 2.5.9 | リモートアクセスVPNを提供すること | 推奨 |
| FR-SVC-012 | chrony | chrony 4.3 | NTPによる時刻同期を行うこと（ntpdは廃止済み） | 必須 |

### ▶️ 3.7 監査（auditd）

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-AUD-001 | auditdを有効化し、システム起動時に自動起動すること | 必須 |
| FR-AUD-002 | sudo実行・ユーザー追加削除・権限変更を監査対象とすること | 必須 |
| FR-AUD-003 | 監査ログ（/var/log/audit/audit.log）を180日以上保管すること | 必須 |
| FR-AUD-004 | 監査ログをSIEM/Syslogサーバーへ転送すること | 推奨 |
| FR-AUD-005 | 監査ルールは /etc/audit/rules.d/ で管理し、重要ファイルへの書き込み・属性変更を記録すること | 必須 |

**主要監査ルール例：**

```
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/sudoers.d/ -p wa -k sudo_changes
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_exec
```

### ▶️ 3.8 バックアップ

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-BAK-001 | OSイメージバックアップを定期取得すること | 必須 |
| FR-BAK-002 | データベースバックアップを日次実施すること | 必須 |
| FR-BAK-003 | ファイルバックアップを日次実施すること | 必須 |
| FR-BAK-004 | バックアップデータを30〜90日保管し、GFS（Grandfather-Father-Son）方式で世代管理すること | 必須 |
| FR-BAK-005 | 半年ごとにリストア試験を実施し、復旧可否を確認すること | 推奨 |

| 項目 | 方針 |
|------|------|
| OSバックアップ | イメージ取得（Snapshot / Clonezilla等） |
| DBバックアップ | 日次（フルまたは増分） |
| ファイルバックアップ | 日次（rsync / tar等） |
| 保管期間 | 30〜90日 |
| 世代管理 | GFS推奨（日次7世代・週次4世代・月次12世代） |
| リストア試験 | 半年毎 |

### ▶️ 3.9 ログ転送・SIEM連携

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-LOG-001 | rsyslogによるリモートSyslogサーバーへの転送を有効化すること | 推奨 |
| FR-LOG-002 | ログ転送はTCP+TLSで暗号化すること | 推奨 |
| FR-LOG-003 | SIEM（OpenSearch / Splunk等）との連携を検討すること | 推奨 |

| 項目 | 推奨 |
|------|------|
| rsyslog転送 | 有効 |
| 転送先 | Syslogサーバー（集約） |
| 転送方式 | TCP + TLS（暗号化必須） |
| 保管・分析 | SIEM連携（OpenSearch / Splunk / Datadog Logs等） |

### ▶️ 3.10 EDR・マルウェア対策

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-EDR-001 | EDR（Endpoint Detection and Response）ソリューションを導入すること | 推奨 |
| FR-EDR-002 | リアルタイム脅威検知・インシデント対応能力を持つ製品を選定すること | 推奨 |

| 項目 | 推奨製品例 |
|------|----------|
| EDR | CrowdStrike Falcon / SentinelOne / Microsoft Defender for Endpoint |
| マルウェア対策 | ClamAV（OSS）/ CrowdStrike Falcon（商用） |
| 監視連携 | EDRアラートをSIEMへ転送 |

### ▶️ 3.11 監視

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-MON-001 | CPU・Memory・Disk使用率・inode使用率を監視すること | 必須 |
| FR-MON-002 | 重要プロセス・サービスの死活監視を実施すること | 必須 |
| FR-MON-003 | TCPポート監視によりサービス応答を確認すること | 必須 |
| FR-MON-004 | SSL/TLS証明書の有効期限を監視すること | 推奨 |
| FR-MON-005 | NTP同期状態を監視すること | 推奨 |

| 監視項目 | 対象 |
|---------|------|
| CPU使用率 | ○ |
| Memory使用率 | ○ |
| Disk使用率 | ○ |
| inode使用率 | ○ |
| Processプロセス監視 | ○ |
| Service死活監視 | ○ |
| TCPポート監視 | ○ |
| SSL証明書期限監視 | ○ |
| NTP同期監視 | ○ |

**推奨監視ツール例：** Zabbix / Prometheus + Grafana / Datadog / Mackerel

### ▶️ 3.12 パッチ管理

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-PAT-001 | セキュリティパッチを月次定例で適用すること | 必須 |
| FR-PAT-002 | CVSS 7.0以上の高リスク脆弱性は緊急対応とし、即時適用すること | 必須 |
| FR-PAT-003 | 本番適用前に検証環境で動作確認すること | 推奨 |
| FR-PAT-004 | カーネル更新はメンテナンス時間帯に実施すること | 必須 |

| 項目 | 方針 |
|------|------|
| 定例パッチ | 月次（毎月第2水曜等に固定） |
| 緊急パッチ | CVSS高リスク（7.0以上）は即時対応 |
| 適用前検証 | 検証環境での動作確認必須 |
| カーネル更新 | メンテナンスウィンドウ内で実施・再起動 |

### ▶️ 3.13 sudo・権限管理

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-SUD-001 | sudo権限はロール（役割）別に分離し、最小権限の原則を適用すること | 必須 |
| FR-SUD-002 | sudo設定は /etc/sudoers.d/ 配下でファイル分割管理すること | 必須 |
| FR-SUD-003 | FreeIPA LDAP連携によるsudo権限の集中管理を推奨すること | 推奨 |

| ロール | 付与権限例 |
|-------|----------|
| 運用管理者（ops） | systemctl / journalctl / 監視コマンド |
| DB管理者（dba） | DBサービス起動停止 / バックアップコマンド |
| AP管理者（app） | Webサーバー起動停止 / アプリデプロイ |
| セキュリティ担当（sec） | audit / aide / fail2ban操作 |

### ▶️ 3.14 サービス自動復旧

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-SVC-013 | 重要サービスはsystemdのRestart機能により自動復旧を設定すること | 推奨 |
| FR-SVC-014 | 自動復旧設定はサービスユニットファイルの `[Service]` セクションで管理すること | 推奨 |

**自動復旧対象サービス例：** httpd / nginx / postfix / named / sshd / chronyd

```ini
[Service]
Restart=always
RestartSec=10
```

### ▶️ 3.15 運用管理サービス

| 要件ID | 要件内容 | 優先度 |
|--------|---------|--------|
| FR-OPS-001 | SSSD/FreeIPAによる集中認証を実装すること | 推奨 |
| FR-OPS-002 | sudo権限のLDAP集中管理（sudo-ldap）を実装すること | 推奨 |
| FR-OPS-003 | SSH公開鍵をFreeIPA/LDAPで集中管理すること | 推奨 |
| FR-OPS-004 | Ansibleによる構成管理自動化を実装すること | 推奨 |
| FR-OPS-005 | 構成管理コードをGitで管理すること | 推奨 |

| サービス | 用途 |
|---------|------|
| SSSD + FreeIPA | 集中認証・ユーザー管理 |
| sudo LDAP連携 | sudo権限の集中管理 |
| SSH公開鍵集中管理 | FreeIPA AuthorizedKeysCommand |
| Ansible | 構成管理・自動化 |
| Git | Ansibleコード・設定ファイル管理 |

---

## 🔷 4. 非機能要件

| 分類 | 要件内容 | 目標値 |
|------|---------|--------|
| 可用性 | システムの年間稼働率 | 99.9%以上 |
| 性能 | Webサーバーレスポンスタイム | 95%tile 500ms以内 |
| セキュリティ | 脆弱性スキャン（OpenSCAP/OpenVAS等）による重大脆弱性 | 0件 |
| 保守性 | OSセキュリティパッチ適用 | 月次（緊急時は即時） |
| バックアップ | データバックアップ間隔 | 日次（フル週次・差分日次） |
| ログ保管 | ログ保管期間 | 最低90日（監査要件に準拠） |
| 時刻精度 | NTP同期精度 | ±100ms以内 |

---

## 🔷 5. 制約事項・前提条件

| 分類 | 内容 |
|------|------|
| OS | AlmaLinux 9.4 / RHEL 9.4（カーネル 5.14.0-427 系） |
| 仮想化 | KVM / VMware vSphere / AWS EC2 等の仮想環境を想定 |
| パッケージ管理 | dnf（yumコマンドはエイリアス扱い） |
| 非対応機能 | OpenLDAPはRHEL9で非対応（FreeIPAまたは389-dsを使用） |
| 非対応機能 | pam_tally2廃止 → pam_faillock使用 |
| 非対応機能 | ntpd廃止 → chrony使用 |
| ネットワーク設定 | ifcfg形式は廃止方向。NetworkManager keyfile形式を推奨 |
| 管理ツール | Ansible 等の構成管理ツールによる自動化を推奨 |
| 法規制 | 個人情報保護法・情報セキュリティポリシーに準拠すること |
