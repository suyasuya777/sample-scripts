# 📘 Linux サーバー構築 基本設計書

> 前提OS：AlmaLinux 9.4 / RHEL 9.4（kernel 5.14.0 系）

---

## 🔷 改訂履歴

| 版数 | 改訂日 | 改訂者 | 改訂内容 |
|------|--------|--------|----------|
| 1.0 | 2025-06-17 | 作成者 | 初版作成 |

---

## 📋 目次

- [📘 Linux サーバー構築 基本設計書](#-linux-サーバー構築-基本設計書)
  - [🔷 改訂履歴](#-改訂履歴)
  - [📋 目次](#-目次)
  - [🔷 1. OS基本設定](#-1-os基本設定)
    - [▶️ 1.1 OS・ハードウェア構成方針](#️-11-osハードウェア構成方針)
    - [▶️ 1.2 ホスト名・タイムゾーン・ロケール](#️-12-ホスト名タイムゾーンロケール)
    - [▶️ 1.3 ブートローダー（GRUB2 + BLS形式）設計方針](#️-13-ブートローダーgrub2--bls形式設計方針)
    - [▶️ 1.4 systemd 設計方針](#️-14-systemd-設計方針)
    - [▶️ 1.5 パッケージ管理方針（RHEL9）](#️-15-パッケージ管理方針rhel9)
  - [🔷 2. カーネル設定（sysctl）](#-2-カーネル設定sysctl)
    - [▶️ 2.1 ネットワークセキュリティ強化](#️-21-ネットワークセキュリティ強化)
    - [▶️ 2.2 カーネル・セキュリティ設定](#️-22-カーネルセキュリティ設定)
  - [🔷 3. ストレージ・ファイルシステム設計](#-3-ストレージファイルシステム設計)
    - [▶️ 3.1 パーティション設計方針](#️-31-パーティション設計方針)
    - [▶️ 3.2 ファイルシステム種別](#️-32-ファイルシステム種別)
  - [🔷 4. ネットワーク基本設計](#-4-ネットワーク基本設計)
  - [🔷 5. ユーザー・認証基本設計](#-5-ユーザー認証基本設計)
    - [▶️ 5.1 ユーザー管理ファイル](#️-51-ユーザー管理ファイル)
  - [🔷 6. セキュリティ基本設計](#-6-セキュリティ基本設計)
    - [▶️ 6.1 SELinux](#️-61-selinux)
    - [▶️ 6.2 ファイアウォール設計方針](#️-62-ファイアウォール設計方針)
    - [▶️ 6.3 SSH強化設計（OpenSSH 8.7 ベース）](#️-63-ssh強化設計openssh-87-ベース)
  - [🔷 7. 主要サービス基本設計](#-7-主要サービス基本設計)
    - [▶️ 7.1 DNSコンテンツサーバー（BIND 9.16 / named）](#️-71-dnsコンテンツサーバーbind-916--named)
    - [▶️ 7.2 DNSキャッシュサーバー（unbound 1.16）](#️-72-dnsキャッシュサーバーunbound-116)
    - [▶️ 7.3 Webサーバー（Apache httpd 2.4.57 / Nginx 1.22）](#️-73-webサーバーapache-httpd-2457--nginx-122)
    - [▶️ 7.4 プロキシ（Squid 5.5）](#️-74-プロキシsquid-55)
    - [▶️ 7.5 ファイル共有（Samba 4.17 / NFS v4.2）](#️-75-ファイル共有samba-417--nfs-v42)
    - [▶️ 7.6 メールサービス（Postfix 3.5.9 / Dovecot 2.3.16）](#️-76-メールサービスpostfix-359--dovecot-2316)
    - [▶️ 7.7 DHCP / ディレクトリ / FTP / VPN](#️-77-dhcp--ディレクトリ--ftp--vpn)
    - [▶️ 7.8 暗号化設計方針](#️-78-暗号化設計方針)
  - [🔷 8. ログ管理基本設計](#-8-ログ管理基本設計)
  - [🔷 9. 監査（auditd）基本設計](#-9-監査auditd基本設計)
  - [🔷 10. 時刻同期冗長化設計](#-10-時刻同期冗長化設計)
  - [🔷 11. バックアップ基本設計](#-11-バックアップ基本設計)
  - [🔷 12. ログ転送・SIEM連携基本設計](#-12-ログ転送siem連携基本設計)
  - [🔷 13. EDR・マルウェア対策基本設計](#-13-edrマルウェア対策基本設計)
  - [🔷 14. 監視基本設計](#-14-監視基本設計)
  - [🔷 15. パッチ管理基本設計](#-15-パッチ管理基本設計)
  - [🔷 16. sudo・権限管理基本設計](#-16-sudo権限管理基本設計)
  - [🔷 17. サービス自動復旧設計](#-17-サービス自動復旧設計)
  - [🔷 18. 運用管理サービス基本設計](#-18-運用管理サービス基本設計)


---


## 🔷 1. OS基本設定

### ▶️ 1.1 OS・ハードウェア構成方針

| 項目 | 設計内容 |
|------|---------|
| 対象OS | **AlmaLinux 9.4** / RHEL 9.4（カーネル 5.14.0-427 系） |
| インストール方式 | 最小インストール（Minimal Install）＋必要パッケージをdnfで追加 |
| 仮想化基盤 | KVM / VMware vSphere / AWS EC2 いずれか |
| ファームウェア | **UEFI（GPTパーティション）を必須**。レガシーBIOS/MBRは非推奨 |
| パッケージ管理 | **DNF 4.14**（yumコマンドはdnfへのシンボリックリンク） |

### ▶️ 1.2 ホスト名・タイムゾーン・ロケール

| 項目 | 設計方針 |
|------|---------|
| ホスト名形式 | `<役割>-<環境>-<連番>.example.com`　例: `web-prod-01.example.com` |
| タイムゾーン | Asia/Tokyo（JST） |
| ロケール | ja_JP.UTF-8 |
| キーボード | jp106 |

### ▶️ 1.3 ブートローダー（GRUB2 + BLS形式）設計方針

| 項目 | 設計方針 |
|------|---------|
| 設定ファイル | `/etc/default/grub`（編集元）、`/boot/grub2/grub.cfg`（生成物・直接編集禁止） |
| BLSエントリ | `/boot/loader/entries/*.conf`（RHEL8以降のBoot Loader Spec形式） |
| タイムアウト | 5秒 |
| カーネルコマンドライン | `quiet audit=1 selinux=1 security=selinux` |
| 設定反映コマンド | `grub2-mkconfig -o /boot/grub2/grub.cfg` |
| EFIパス | `/boot/efi/EFI/almalinux/grub.cfg`（UEFI環境） |

> **注意**：RHEL9では `GRUB_ENABLE_BLSCFG=true` がデフォルト。BLSエントリは `grubby` コマンドで管理推奨。

### ▶️ 1.4 systemd 設計方針

| 項目 | 設計方針 |
|------|---------|
| バージョン | systemd **252**（RHEL9標準） |
| デフォルトターゲット | `multi-user.target`（サーバー用途） |
| 不要サービス | `bluetooth.service` / `cups.service` / `avahi-daemon.service` 等を disable |
| ログ設定 | journald を使用、永続化ログ（`/var/log/journal`）を有効化 |
| サービス自動起動 | 必要サービスのみ `systemctl enable --now` で有効化 |
| タイマー | 定期ジョブは **systemd timer** を優先推奨（cronie も利用可） |

### ▶️ 1.5 パッケージ管理方針（RHEL9）

| 項目 | 設計方針 |
|------|---------|
| パッケージ管理ツール | **dnf**（yumはdnfへのエイリアス） |
| リポジトリ設定 | `/etc/yum.repos.d/*.repo`（BaseOS / AppStream / extras-common） |
| EPELリポジトリ | `dnf install epel-release`（AlmaLinux9の場合） |
| アップデート方針 | `dnf update --security` でセキュリティパッチのみ適用 |
| モジュール管理 | DNF Modules（AppStreamのStream/Profile管理） |

---

## 🔷 2. カーネル設定（sysctl）

### ▶️ 2.1 ネットワークセキュリティ強化

| パラメーター | 設計値 | 目的 |
|------------|--------|------|
| `net.ipv4.ip_forward` | 0 | IPフォワーディング無効（ルーター用途は1） |
| `net.ipv4.conf.all.send_redirects` | 0 | ICMPリダイレクト送信無効 |
| `net.ipv4.conf.all.accept_redirects` | 0 | ICMPリダイレクト受信無効 |
| `net.ipv4.conf.all.accept_source_route` | 0 | ソースルーティング無効 |
| `net.ipv4.tcp_syncookies` | 1 | SYN Flood攻撃対策 |
| `net.ipv4.conf.all.rp_filter` | 1 | リバースパスフィルタリング有効 |
| `net.ipv4.conf.all.log_martians` | 1 | 不正パケットをログ記録 |
| `net.ipv4.icmp_echo_ignore_broadcasts` | 1 | ブロードキャストpingを無視 |
| `net.ipv6.conf.all.disable_ipv6` | 1（IPv6不要時） | IPv6無効化 |

### ▶️ 2.2 カーネル・セキュリティ設定

| パラメーター | 設計値 | 目的 |
|------------|--------|------|
| `kernel.sysrq` | 0 | SysRqキー無効化 |
| `kernel.core_uses_pid` | 1 | コアダンプにPIDを付与 |
| `kernel.dmesg_restrict` | 1 | 一般ユーザーのdmesg参照を制限 |
| `kernel.perf_event_paranoid` | 2 | perfイベントへのアクセス制限 |
| `kernel.randomize_va_space` | 2 | ASLR有効（フルランダム化） |
| `fs.suid_dumpable` | 0 | SUID実行ファイルのコアダンプ無効 |
| `fs.protected_hardlinks` | 1 | ハードリンク保護 |
| `fs.protected_symlinks` | 1 | シンボリックリンク保護 |
| `vm.swappiness` | 10（DB用途）/ 60（一般） | スワップ使用率の調整 |

---

## 🔷 3. ストレージ・ファイルシステム設計

### ▶️ 3.1 パーティション設計方針

| マウントポイント | 推奨サイズ | ファイルシステム | 役割 |
|---------------|----------|---------------|------|
| `/boot` | 1GB | xfs | カーネル・ブートファイル |
| `/boot/efi` | 600MB | vfat（FAT32） | EFIシステムパーティション（UEFI必須） |
| `/` | 20GB以上 | **xfs**（RHEL9デフォルト） | ルートパーティション |
| `/var` | 10GB以上 | xfs | ログ・スプール |
| `/home` | 用途による | xfs | ユーザーホームディレクトリ |
| `/tmp` | 5GB | xfs | 一時ファイル（noexec推奨） |
| `swap` | 物理メモリ×1〜2倍（最大16GB） | swap | スワップ領域 |

> **RHEL9注意**：RHEL9では zram によるメモリ内スワップがデフォルト有効。`zram-generator` の設定確認を推奨。

### ▶️ 3.2 ファイルシステム種別

| ファイルシステム | 特徴 | RHEL9での状況 |
|---------------|------|-------------|
| **XFS** | ジャーナリング、動的inode、大容量向け | **RHEL9デフォルト。本番推奨** |
| ext4 | ジャーナリング、安定性高い | サポート継続。汎用用途 |
| btrfs | スナップショット対応 | RHEL9では**テクノロジープレビュー**（本番非推奨） |
| vfat | FAT32 | EFIパーティション専用 |

---

## 🔷 4. ネットワーク基本設計

| 項目 | 設計方針 |
|------|---------|
| 管理ツール | **NetworkManager 1.42**（nmcliコマンド使用） |
| 設定ファイル形式 | **keyfile形式**（`/etc/NetworkManager/system-connections/`）を推奨 |
| 旧ifcfg形式 | `/etc/sysconfig/network-scripts/` は **RHEL9でdeprecated**（削除予定） |
| NIC命名規則 | Predictable Network Interface Names（例: `ens3`, `enp3s0`）を使用 |
| DNS管理 | NetworkManager経由で `/etc/resolv.conf` を自動管理 |
| 名前解決順序 | `/etc/nsswitch.conf` にて `files → dns` の順に設定 |
| IPv6 | 原則無効化（必要な場合は別途設計） |

---

## 🔷 5. ユーザー・認証基本設計

| 項目 | 設計方針 |
|------|---------|
| rootログイン | SSH・コンソールともに直接ログイン禁止。sudo経由のみ許可 |
| 管理ユーザー | wheelグループに所属するユーザーで管理 |
| パスワードポリシー | `/etc/security/pwquality.conf` で管理。最小12文字（NIST SP800-63準拠） |
| アカウントロック | **pam_faillock**（`/etc/security/faillock.conf`）で管理。※pam_tally2はRHEL9廃止済み |
| SSH認証 | 公開鍵認証のみ（パスワード認証無効）。Ed25519鍵を推奨 |
| PAMバージョン | **PAM 1.5.1**（RHEL9標準） |
| LDAP連携 | **SSSD + FreeIPA / 389-ds** で集中認証。※OpenLDAPはRHEL9非対応 |

### ▶️ 5.1 ユーザー管理ファイル

| ファイル | 役割 |
|---------|------|
| `/etc/passwd` | ユーザーアカウント情報 |
| `/etc/shadow` | パスワードハッシュ・有効期限（ハッシュアルゴリズム：sha512 → yescrypt推奨） |
| `/etc/group` | グループ情報 |
| `/etc/sudoers` / `/etc/sudoers.d/` | sudo権限設定 |
| `/etc/skel/` | 新規ユーザーホームディレクトリ雛形 |
| `/etc/security/pwquality.conf` | パスワードポリシー（libpwquality） |
| `/etc/security/faillock.conf` | アカウントロック設定（pam_faillock） |

---

## 🔷 6. セキュリティ基本設計

### ▶️ 6.1 SELinux

| 項目 | 設計方針 |
|------|---------|
| バージョン | SELinux **3.5**（RHEL9標準） |
| 動作モード | **enforcing**（`/etc/selinux/config` で `SELINUX=enforcing`） |
| ポリシー | **targeted**（主要サービスを対象） |
| ラベル管理 | `semanage` コマンドで管理（`chcon` は一時的な変更のみ） |
| ブール値管理 | `getsebool -a` / `setsebool -P` で永続変更 |
| トラブルシュート | `audit2why` / `audit2allow` で対応 |

### ▶️ 6.2 ファイアウォール設計方針

| 項目 | 設計内容 |
|------|---------|
| ツール | **firewalld 1.2**（バックエンド：**nftables 1.0.4**） |
| **注意** | **iptablesコマンドはnftablesのレガシーラッパー。firewalldで統一管理** |
| 管理方法 | `firewall-cmd` コマンドまたは `firewall-config` GUIツール |
| ゾーン設計 | public（外部）/ internal（内部）/ dmz（DMZ）を用途に応じて使い分け |

**ポート許可設計：**

| サービス | プロトコル | ポート | ゾーン |
|---------|----------|------|--------|
| SSH | TCP | 22（変更推奨） | internal |
| HTTP | TCP | 80 | public |
| HTTPS | TCP | 443 | public |
| DNS | TCP/UDP | 53 | internal |
| SMTP | TCP | 25 | internal |
| NTP | UDP | 123 | internal |
| その他 | — | — | 原則DROP |

### ▶️ 6.3 SSH強化設計（OpenSSH 8.7 ベース）

| 設定項目 | 設定値 | 備考 |
|---------|--------|------|
| Port | 22（または変更） | デフォルトポート変更を検討 |
| PermitRootLogin | no | root直接ログイン禁止 |
| PasswordAuthentication | no | パスワード認証無効 |
| PubkeyAuthentication | yes | 公開鍵認証有効 |
| HostKey（推奨順） | ed25519 → ecdsa → rsa | Ed25519を優先 |
| AllowUsers / AllowGroups | 管理ユーザーのみ | ログイン許可制限 |
| MaxAuthTries | 3 | 認証失敗最大回数 |
| ClientAliveInterval | 300 | アイドルタイムアウト（秒） |
| X11Forwarding | no | X11フォワーディング禁止 |

---

## 🔷 7. 主要サービス基本設計

### ▶️ 7.1 DNSコンテンツサーバー（BIND 9.16 / named）

| 項目 | 設計方針 |
|------|---------|
| バージョン | **BIND 9.16**（RHEL9 AppStream） |
| 役割 | **権威DNS**（コンテンツサーバー）。外部・内部クライアントへゾーン情報を応答する |
| 動作モード | `recursion no`（再帰問い合わせ禁止）。権威応答のみ提供 |
| 設定ファイル | `/etc/named.conf`（メイン）、`/var/named/`（ゾーンファイル） |
| ゾーン管理 | プライマリ（`type primary`）／セカンダリ（`type secondary`）構成で冗長化 |
| DNSSEC | `dnssec-policy` ディレクティブ（BIND 9.16の新機能）を使用。KSK/ZSK自動ロールオーバー |
| セキュリティ | `allow-transfer { ★セカンダリDNS-IP; };` でゾーン転送先を制限 |
| **注意** | BIND9.16で `dnssec-enable` / `dnssec-lookaside` は廃止。`dnssec-validation auto;` のみ使用 |

### ▶️ 7.2 DNSキャッシュサーバー（unbound 1.16）

| 項目 | 設計方針 |
|------|---------|
| バージョン | **unbound 1.16**（RHEL9 AppStream） |
| 役割 | **再帰リゾルバー**（キャッシュDNS）。内部クライアントの名前解決要求を受け付けBINDや外部DNSへフォワード・再帰解決する |
| 動作モード | `do-recursion: yes`。内部NWからの再帰問い合わせのみ受付 |
| 設定ファイル | `/etc/unbound/unbound.conf`（メイン）、`/etc/unbound/conf.d/`（分割設定） |
| アクセス制御 | `access-control: ★内部NW allow`（外部からの問い合わせは拒否） |
| フォワード設定 | 内部ドメインはBIND（コンテンツサーバー）へフォワード。それ以外は外部DNSまたはルートヒントで解決 |
| DNSSEC検証 | `val-permissive-mode: no`（DNSSEC検証を厳格化）。BINDが署名した内部ゾーンも検証対象 |
| キャッシュ | `cache-max-ttl: 86400` / `cache-min-ttl: 0`（TTL範囲制御）。`prefetch: yes` 推奨 |
| セキュリティ | `hide-identity: yes` / `hide-version: yes` でサーバー情報を非表示 |

### ▶️ 7.3 Webサーバー（Apache httpd 2.4.57 / Nginx 1.22）

| 項目 | 設計方針 |
|------|---------|
| Apacheバージョン | **httpd 2.4.57**（RHEL9 AppStream） |
| Nginxバージョン | **Nginx 1.22**（RHEL9 AppStream） |
| TLSバージョン | **TLS 1.2 / TLS 1.3**（SSLv3/TLS1.0/1.1は明示的に無効化） |
| 証明書 | X.509 v3。ECDSA（P-256）または RSA 2048bit以上 |
| HTTP/2 | Apache: `mod_http2`、Nginx: デフォルト対応 |
| セキュリティヘッダー | HSTS / X-Frame-Options / X-Content-Type-Options / CSP |

### ▶️ 7.4 プロキシ（Squid 5.5）

| 項目 | 設計方針 |
|------|---------|
| バージョン | **Squid 5.5**（RHEL9 AppStream） |
| 設定ファイル | `/etc/squid/squid.conf` |
| アクセス制御 | ACLで許可クライアントIPを制限、ブラックリストURLをフィルタリング |
| TLS | SSLバンプ対応（`ssl-bump`） |

### ▶️ 7.5 ファイル共有（Samba 4.17 / NFS v4.2）

| 項目 | 設計方針 |
|------|---------|
| Sambaバージョン | **Samba 4.17**（RHEL9 AppStream） |
| 対応プロトコル | **SMB 3.1.1**（SMB1は廃止済み、デフォルト無効） |
| NFSバージョン | **NFSv4.2**（NFSv2/v3は非推奨）。`/etc/nfs.conf` で管理 |
| NFS設定ファイル | `/etc/nfs.conf`（RHEL9）、`/etc/exports`（エクスポート定義） |

### ▶️ 7.6 メールサービス（Postfix 3.5.9 / Dovecot 2.3.16）

| 項目 | 設計方針 |
|------|---------|
| Postfixバージョン | **Postfix 3.5.9**（RHEL9 AppStream） |
| Dovecotバージョン | **Dovecot 2.3.16**（RHEL9 AppStream） |
| SMTP TLS | STARTTLS必須（`smtpd_tls_security_level = encrypt`） |
| IMAP/POP3 | **IMAPS（993）/ POP3S（995）のみ許可**。平文587は内部のみ |
| スパム対策 | DKIM（opendkim）/ SPF / DMARC レコード設定 |
| メールボックス | Maildir形式を使用 |

### ▶️ 7.7 DHCP / ディレクトリ / FTP / VPN

| サービス | バージョン | 設計方針 |
|---------|-----------|---------|
| **DHCP（isc-dhcp-server）** | ISC DHCP 4.4.2 | `/etc/dhcp/dhcpd.conf`。KEA DHCPへの移行も検討 |
| **FreeIPA / 389-ds** | FreeIPA 4.10 / 389-ds 2.3 | **RHEL9ではOpenLDAP非対応**。FreeIPAまたは389-dsを使用 |
| **SSSD** | SSSD 2.8 | FreeIPA / AD連携の認証クライアント |
| **vsftpd（FTP）** | vsftpd 3.0.5 | 匿名アクセス禁止。**FTPS（Explicit TLS）必須** |
| **OpenVPN** | OpenVPN 2.5.9 | PKI構築（Easy-RSA 3.x）。**tls-crypt推奨（tls-auth旧方式）** |
| **chrony（NTP）** | chrony 4.3 | **ntpdは廃止済み**。`/etc/chrony.conf` で管理 |
| **AIDE** | AIDE 0.16 | ファイル整合性監視。初期DB作成後に定期チェック |
| **Fail2ban** | Fail2ban 1.0 | SSH/httpd等の失敗ログ監視。firewalldと連携 |

### ▶️ 7.8 暗号化設計方針

| 種別 | 技術・バージョン | 設計方針 |
|------|--------------|---------|
| ディスク暗号化 | **LUKS2**（cryptsetup 2.4） | **LUKS1は非推奨。LUKS2（Argon2idキー導出）を使用** |
| ファイル暗号化 | **GnuPG 2.3.3** | ファイル・メールの暗号化・署名。Ed25519鍵推奨 |
| SSL/TLS証明書 | X.509 v3（TLS 1.2/1.3） | ECDSA P-256またはRSA 2048bit以上 |
| DNSSEC | BIND 9.16 `dnssec-policy` | KSK/ZSK自動ロールオーバー（BIND9.16の新機能） |
| SSH鍵 | **Ed25519**（最優先）/ ECDSA / RSA 4096bit | RSA 1024/2048bitは非推奨 |

---

## 🔷 8. ログ管理基本設計

| ログ種別 | パス | 保管期間 | ローテーション |
|---------|------|---------|-------------|
| システムログ | `/var/log/messages` | 90日 | 日次・7世代 |
| 認証ログ | `/var/log/secure` | 90日 | 日次・7世代 |
| cronログ | `/var/log/cron` | 30日 | 日次・7世代 |
| メールログ | `/var/log/maillog` | 90日 | 日次・7世代 |
| Webアクセスログ | `/var/log/httpd/access.log` | 90日 | 日次・30世代 |
| Webエラーログ | `/var/log/httpd/error.log` | 90日 | 日次・30世代 |
| 監査ログ（auditd） | `/var/log/audit/audit.log` | 180日 | サイズベース（50MB） |
| journald | `/var/log/journal`（永続化） | 30日 | サイズ制限（1GB） |
| DNFトランザクション | `/var/log/dnf.log` | 90日 | 日次 |

> **RHEL9注意**：journaldが一次ログ収集を担う。rsyslogはjournaldからの転送で動作（`imjournal` モジュール使用）。

---

## 🔷 9. 監査（auditd）基本設計

| 項目 | 設計方針 |
|------|---------|
| auditdバージョン | **audit 3.0.7**（RHEL9標準） |
| 動作状態 | **有効**（起動時に自動起動 `systemctl enable --now auditd`） |
| ログ保管期間 | **180日以上**（監査要件に準拠） |
| ログパス | `/var/log/audit/audit.log` |
| ローテーション | サイズベース（50MB×5世代）。`/etc/audit/auditd.conf` で管理 |
| ログ転送 | auditspd-plugins / rsyslog経由でSIEM/Syslogサーバーへ転送 |
| ルール管理 | `/etc/audit/rules.d/` 配下に用途別ファイルで管理 |

**監査対象の設計方針：**

| 監査対象 | キー名 | 重要度 |
|---------|--------|--------|
| /etc/passwd への書き込み・属性変更 | passwd_changes | 高 |
| /etc/shadow への書き込み・属性変更 | shadow_changes | 高 |
| /etc/sudoers / sudoers.d/ への書き込み | sudo_changes | 高 |
| /etc/ssh/ への書き込み | sshd_config | 高 |
| rootによるコマンド実行（execve） | root_exec | 中 |
| システムコール（setuid/setgid） | privilege_escalation | 中 |
| ファイルシステムマウント | mount_ops | 中 |
| ネットワーク設定変更 | network_config | 中 |

**主要監査ルール（`/etc/audit/rules.d/99-custom.rules`）：**

```
# 不変設定（カーネルへの書き込み禁止）
-e 2

# ユーザー・認証関連
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/group -p wa -k group_changes
-w /etc/gshadow -p wa -k gshadow_changes

# sudo / 特権管理
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/sudoers.d/ -p wa -k sudo_changes

# SSH設定
-w /etc/ssh/sshd_config -p wa -k sshd_config

# rootコマンド実行
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_exec
-a always,exit -F arch=b32 -S execve -F euid=0 -k root_exec

# 特権昇格
-a always,exit -F arch=b64 -S setuid -S setgid -k privilege_escalation
```

---

## 🔷 10. 時刻同期冗長化設計

| 項目 | 設計方針 |
|------|---------|
| NTPサービス | **chrony 4.3**（RHEL9標準。ntpdは廃止済み） |
| NTPサーバー数 | **3台以上**を設定し冗長化 |
| 外部同期先 | **NICTサーバー**（ntp.nict.jp）または社内上位NTP |
| 内部NTPサーバー | 3台以上の内部NTPサーバーで分散 |
| chronyd起動監視 | **必須**（監視ツールからの死活確認） |
| NTS対応 | Network Time Security（ntsdumpdir設定）を検討 |

**NTPサーバー構成例（`/etc/chrony.conf`）：**

```
# 内部NTPサーバー（冗長化）
server ntp1.example.local iburst prefer
server ntp2.example.local iburst
server ntp3.example.local iburst

# 内部NTPが不達の場合のフォールバック（NICT公開NTP）
pool ntp.nict.jp iburst

# ローカル時刻源（上位NTP不達時）
local stratum 10
```

| 項目 | 推奨 |
|------|------|
| NTPサーバー数 | 3台以上 |
| 外部同期 | NICTまたは社内上位NTP |
| chronyd起動監視 | 必須（`chronyc tracking` で確認） |
| NTP同期精度目標 | ±100ms以内 |

---

## 🔷 11. バックアップ基本設計

| 項目 | 設計方針 |
|------|---------|
| OSバックアップ | イメージ取得（仮想環境スナップショット / Clonezilla等） |
| DBバックアップ | 日次（論理バックアップ：mysqldump / pg_dump等） |
| ファイルバックアップ | 日次（rsync / tar.gz等） |
| 保管期間 | 30〜90日（要件に応じて設定） |
| 世代管理 | **GFS（Grandfather-Father-Son）方式推奨** |
| リストア試験 | **半年ごと**に実施し、RTO/RPO達成を確認 |
| バックアップ先 | オフサイトストレージまたはオブジェクトストレージ（S3等）を推奨 |

**GFS世代管理設計：**

| 周期 | 世代数 | 保管期間 |
|------|--------|---------|
| 日次フル or 増分 | 7世代 | 1週間 |
| 週次フル | 4世代 | 1ヶ月 |
| 月次フル | 12世代 | 1年 |

---

## 🔷 12. ログ転送・SIEM連携基本設計

| 項目 | 設計方針 |
|------|---------|
| ログ転送ツール | **rsyslog**（imjournalモジュール経由） |
| 転送プロトコル | **TCP + TLS**（平文転送禁止） |
| 転送先 | 集約Syslogサーバー / SIEM |
| SIEM候補 | OpenSearch（Logstash + OpenSearch Dashboards）/ Splunk / Datadog Logs |
| 転送対象ログ | authpriv / kern / audit / Webアクセスログ |
| 転送ポート | 514（TCP+TLS）または 6514（RFC 5425準拠） |

**rsyslogリモート転送設定方針（RainerScript形式）：**

```
action(type="omfwd"
       target="★syslogサーバーIP"
       port="6514"
       protocol="tcp"
       StreamDriver="gtls"
       StreamDriverMode="1"
       StreamDriverAuthMode="x509/name")
```

---

## 🔷 13. EDR・マルウェア対策基本設計

| 項目 | 設計方針 |
|------|---------|
| EDR | CrowdStrike Falcon / SentinelOne / Microsoft Defender for Endpoint から選定 |
| マルウェア対策 | ClamAV（OSS、最小構成）または商用EDRのAV機能を使用 |
| 定義ファイル更新 | 自動更新（日次以上） |
| アラート通知 | EDRコンソールアラート + SIEM転送 |
| エージェント監視 | EDRエージェントの死活監視を実施 |

> **注意**：SELinuxとEDRエージェントの競合が発生する場合、SELinuxポリシーの追加設定が必要。`audit2allow` で対応ポリシーを生成すること。

---

## 🔷 14. 監視基本設計

| 監視項目 | 閾値（警告） | 閾値（重大） | 監視間隔 |
|---------|-----------|-----------|---------|
| CPU使用率 | 80% | 95% | 1分 |
| Memory使用率 | 80% | 95% | 1分 |
| Disk使用率 | 80% | 90% | 5分 |
| inode使用率 | 80% | 90% | 5分 |
| Load Average | CPU×2 | CPU×4 | 1分 |
| プロセス監視 | 停止検知 | — | 1分 |
| サービス死活 | 停止検知 | — | 1分 |
| TCPポート応答 | タイムアウト | — | 1分 |
| SSL証明書期限 | 30日前 | 7日前 | 1日 |
| NTP同期状態 | ±100ms超 | — | 5分 |

**推奨監視ツール：**

| ツール | 用途 |
|--------|------|
| **Zabbix** | エージェント型監視（インフラ全般） |
| **Prometheus + Grafana** | メトリクス収集・可視化 |
| **Datadog** | クラウドネイティブ監視・APM |
| **Mackerel** | 国産SaaS監視（日本語サポート） |
| **Alertmanager** | Prometheusアラート管理 |

---

## 🔷 15. パッチ管理基本設計

| 項目 | 設計方針 |
|------|---------|
| 定例パッチ | **月次**（毎月第2水曜等のメンテナンスウィンドウに固定） |
| 緊急パッチ | CVSS Score **7.0以上**の高リスク脆弱性は即時対応 |
| 適用前検証 | **検証環境**での動作確認必須（本番適用は1週間後を原則） |
| カーネル更新 | メンテナンスウィンドウ内で実施（再起動を伴うため事前周知必要） |
| 脆弱性情報収集 | JVN（Japan Vulnerability Notes）/ RedHat Security Advisory定期確認 |
| パッチ適用コマンド | `dnf update --security`（セキュリティ限定）/ `dnf update`（全体） |

**適用フロー：**

1. 脆弱性情報収集（JVN / RedHat SA）
2. 影響範囲確認
3. 検証環境で適用・動作確認
4. 本番適用（メンテナンスウィンドウ）
5. 適用後確認（サービス正常稼働確認）
6. 記録・報告

---

## 🔷 16. sudo・権限管理基本設計

| 項目 | 設計方針 |
|------|---------|
| 管理方法 | `/etc/sudoers.d/` 配下にロール別ファイルで分割管理 |
| 直接編集禁止 | `/etc/sudoers` は `visudo` 以外での直接編集禁止 |
| LDAP連携 | FreeIPAのsudo rulsによる集中管理（推奨） |
| ログ記録 | sudo実行はauthprivファシリティ・auditdで記録 |

**ロール別sudo設計：**

| ロール | グループ | sudoers.dファイル | 付与コマンド例 |
|-------|---------|-----------------|------------|
| 運用管理者 | ops | `/etc/sudoers.d/ops` | systemctl, journalctl, nmcli |
| DB管理者 | dba | `/etc/sudoers.d/dba` | mysqldump, pg_dump, DBサービス起動停止 |
| AP管理者 | app | `/etc/sudoers.d/app` | httpd/nginx 起動停止, deploy スクリプト |
| セキュリティ担当 | sec | `/etc/sudoers.d/sec` | aide, fail2ban-client, auditctl |
| 一般ユーザー | — | — | sudo権限なし |

**`/etc/sudoers.d/ops` 例：**

```
%ops ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/journalctl, /usr/sbin/nmcli
```

---

## 🔷 17. サービス自動復旧設計

systemdの `Restart` ディレクティブを活用し、重要サービスの自動復旧を設定する。

| 項目 | 設計方針 |
|------|---------|
| 対象サービス | httpd / nginx / postfix / named / unbound / sshd / chronyd / auditd |
| 設定方式 | Drop-in設定ファイル（`/etc/systemd/system/★.service.d/restart.conf`）で管理 |
| 再起動回数制限 | StartLimitBurst / StartLimitIntervalSec で無限ループを防止 |
| アラート連携 | 自動復旧失敗時に監視ツールへアラートを送出 |

**Drop-in設定ファイル例（`/etc/systemd/system/httpd.service.d/restart.conf`）：**

```ini
[Service]
Restart=always
RestartSec=10

[Unit]
StartLimitBurst=5
StartLimitIntervalSec=60
```

**自動復旧設計一覧：**

| サービス | Restart | RestartSec | 備考 |
|---------|---------|-----------|------|
| httpd | always | 10秒 | Webサービス継続性確保 |
| nginx | always | 10秒 | Webサービス継続性確保 |
| postfix | always | 10秒 | メール配送継続 |
| named | always | 10秒 | DNS継続性確保（権威DNS） |
| unbound | always | 10秒 | DNS継続性確保（キャッシュDNS） |
| sshd | always | 5秒 | 管理接続確保（慎重に設定） |
| chronyd | always | 30秒 | 時刻同期継続 |

---

## 🔷 18. 運用管理サービス基本設計

| サービス | バージョン | 設計方針 |
|---------|-----------|---------|
| **SSSD** | SSSD 2.8 | FreeIPA連携による集中認証クライアント |
| **FreeIPA** | FreeIPA 4.10 | LDAP + Kerberos + DNS + sudo集中管理 |
| **sudo LDAP連携** | FreeIPA sudo rules | FreeIPA上でsudoルールを集中管理 |
| **SSH公開鍵集中管理** | FreeIPA `AuthorizedKeysCommand` | 公開鍵をFreeIPAで一元管理 |
| **Ansible** | Ansible 2.14以上 | サーバー構成管理・プロビジョニング自動化 |
| **Git** | Git 2.39以上 | Ansibleコード・設定ファイルのバージョン管理 |

**SSH公開鍵集中管理設定（`/etc/ssh/sshd_config` 追記）：**

```
AuthorizedKeysCommand /usr/bin/sss_ssh_authorizedkeys %u
AuthorizedKeysCommandUser nobody
```

**Ansible構成管理ディレクトリ構成例：**

```
ansible/
├── inventory/
│   ├── production
│   └── staging
├── roles/
│   ├── common/      # OS基本設定
│   ├── security/    # SELinux / firewalld / SSH
│   ├── monitoring/  # Zabbix / Prometheus agent
│   └── backup/      # バックアップスクリプト
├── playbooks/
│   ├── site.yml
│   └── patch.yml
└── group_vars/
    └── all.yml
```
