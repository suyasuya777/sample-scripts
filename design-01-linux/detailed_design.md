# 📘 Linux サーバー構築 詳細設計書（パラメータリスト）

> 前提OS：AlmaLinux 9.4 / RHEL 9.4（kernel 5.14.0 系）  
> ※「★設定値」はプロジェクト固有の実際の値を記入すること。

---

## 🔷 改訂履歴

| 版数 | 改訂日 | 改訂者 | 改訂内容 |
|------|--------|--------|----------|
| 1.0 | 2025-06-17 | 作成者 | 初版作成 |

---

## 📋 目次

- [📘 Linux サーバー構築 詳細設計書（パラメータリスト）](#-linux-サーバー構築-詳細設計書パラメータリスト)
  - [🔷 改訂履歴](#-改訂履歴)
  - [📋 目次](#-目次)
  - [🔷 1. OS基本設定パラメーター](#-1-os基本設定パラメーター)
    - [▶️ 1.1 システム基本情報](#️-11-システム基本情報)
    - [▶️ 1.2 GRUB2 パラメーター（`/etc/default/grub`）](#️-12-grub2-パラメーターetcdefaultgrub)
    - [▶️ 1.3 systemd 設定パラメーター](#️-13-systemd-設定パラメーター)
  - [🔷 2. カーネルパラメーター（`/etc/sysctl.d/99-custom.conf`）](#-2-カーネルパラメーターetcsysctld99-customconf)
    - [▶️ 2.1 ネットワークセキュリティ](#️-21-ネットワークセキュリティ)
    - [▶️ 2.2 カーネルセキュリティ・パフォーマンス](#️-22-カーネルセキュリティパフォーマンス)
  - [🔷 3. ストレージ・ファイルシステムパラメーター](#-3-ストレージファイルシステムパラメーター)
    - [▶️ 3.1 パーティション構成（`/etc/fstab`）](#️-31-パーティション構成etcfstab)
  - [🔷 4. ネットワーク設定パラメーター](#-4-ネットワーク設定パラメーター)
    - [▶️ 4.1 NIC設定（NetworkManager keyfile形式）](#️-41-nic設定networkmanager-keyfile形式)
    - [▶️ 4.2 `/etc/hosts`](#️-42-etchosts)
    - [▶️ 4.3 `/etc/resolv.conf`](#️-43-etcresolvconf)
    - [▶️ 4.4 `/etc/nsswitch.conf`（名前解決順序）](#️-44-etcnsswitchconf名前解決順序)
  - [🔷 5. SSH設定パラメーター（`/etc/ssh/sshd_config`）](#-5-ssh設定パラメーターetcsshsshd_config)
  - [🔷 6. ユーザー・PAM設定パラメーター](#-6-ユーザーpam設定パラメーター)
    - [▶️ 6.1 パスワードポリシー（`/etc/security/pwquality.conf`）](#️-61-パスワードポリシーetcsecuritypwqualityconf)
    - [▶️ 6.2 アカウントロック（`/etc/security/faillock.conf`）](#️-62-アカウントロックetcsecurityfaillockconf)
    - [▶️ 6.3 パスワード有効期限（`/etc/login.defs`）](#️-63-パスワード有効期限etclogindefs)
  - [🔷 7. DNS設定パラメーター（BIND 9.16 / named）](#-7-dns設定パラメーターbind-916--named)
    - [▶️ 7.1 `/etc/named.conf` 主要パラメーター](#️-71-etcnamedconf-主要パラメーター)
    - [▶️ 7.2 DNSSEC設定（BIND 9.16 `dnssec-policy`）](#️-72-dnssec設定bind-916-dnssec-policy)
    - [▶️ 7.3 ゾーンファイルパラメーター（正引き）](#️-73-ゾーンファイルパラメーター正引き)
  - [🔷 8. Webサーバー設定パラメーター](#-8-webサーバー設定パラメーター)
    - [▶️ 8.1 Apache（`/etc/httpd/conf/httpd.conf`）](#️-81-apacheetchttpdconfhttpdconf)
    - [▶️ 8.2 SSL/TLS設定（`/etc/httpd/conf.d/ssl.conf`）](#️-82-ssltls設定etchttpdconfdsslconf)
    - [▶️ 8.3 Nginx（`/etc/nginx/nginx.conf`）](#️-83-nginxetcnginxnginxconf)
  - [🔷 9. ファイル共有設定パラメーター](#-9-ファイル共有設定パラメーター)
    - [▶️ 9.1 Samba（`/etc/samba/smb.conf`）- \[global\]セクション](#️-91-sambaetcsambasmbconf--globalセクション)
    - [▶️ 9.2 Samba 共有定義（\[share\]セクション）](#️-92-samba-共有定義shareセクション)
    - [▶️ 9.3 NFS（`/etc/nfs.conf` + `/etc/exports`）](#️-93-nfsetcnfsconf--etcexports)
  - [🔷 10. メールサービス設定パラメーター](#-10-メールサービス設定パラメーター)
    - [▶️ 10.1 Postfix（`/etc/postfix/main.cf`）](#️-101-postfixetcpostfixmaincf)
    - [▶️ 10.2 Dovecot（`/etc/dovecot/dovecot.conf`）](#️-102-dovecotetcdovecotdovecotconf)
  - [🔷 11. DHCPサービス設定パラメーター（`/etc/dhcp/dhcpd.conf`）](#-11-dhcpサービス設定パラメーターetcdhcpdhcpdconf)
  - [🔷 12. FTPサービス設定パラメーター（`/etc/vsftpd/vsftpd.conf`）](#-12-ftpサービス設定パラメーターetcvsftpdvsftpdconf)
  - [🔷 13. OpenVPN設定パラメーター（`/etc/openvpn/server/server.conf`）](#-13-openvpn設定パラメーターetcopenvpnserverserverconf)
  - [🔷 14. セキュリティ設定パラメーター](#-14-セキュリティ設定パラメーター)
    - [▶️ 14.1 SELinux（`/etc/selinux/config`）](#️-141-selinuxetcselinuxconfig)
    - [▶️ 14.2 firewalld 許可サービス一覧](#️-142-firewalld-許可サービス一覧)
  - [🔷 15. プロキシ設定パラメーター（`/etc/squid/squid.conf`）](#-15-プロキシ設定パラメーターetcsquidsquidconf)
  - [🔷 16. NTP設定パラメーター（`/etc/chrony.conf`）](#-16-ntp設定パラメーターetcchronyconf)
  - [🔷 17. ファイル整合性監視パラメーター（`/etc/aide.conf`）](#-17-ファイル整合性監視パラメーターetcaideconf)
  - [🔷 18. Fail2ban設定パラメーター（`/etc/fail2ban/jail.d/custom.conf`）](#-18-fail2ban設定パラメーターetcfail2banjaildcustomconf)
  - [🔷 19. ディレクトリサービス設定パラメーター](#-19-ディレクトリサービス設定パラメーター)
    - [▶️ 19.1 FreeIPA（`ipa` コマンドで管理）](#️-191-freeipaipa-コマンドで管理)
    - [▶️ 19.2 SSSD（`/etc/sssd/sssd.conf`）](#️-192-sssdetcsssdsssdconf)
  - [🔷 20. ログ・ジョブスケジューラー設定パラメーター](#-20-ログジョブスケジューラー設定パラメーター)
    - [▶️ 20.1 rsyslog（`/etc/rsyslog.conf`）](#️-201-rsyslogetcrsyslogconf)
    - [▶️ 20.2 logrotate（`/etc/logrotate.d/`）](#️-202-logrotateetclogrotated)
    - [▶️ 20.3 ジョブスケジューラー設定](#️-203-ジョブスケジューラー設定)
  - [🔷 21. 監査（auditd）設定パラメーター](#-21-監査auditd設定パラメーター)
    - [▶️ 21.1 auditd設定（`/etc/audit/auditd.conf`）](#️-211-auditd設定etcauditauditdconf)
    - [▶️ 21.2 監査ルール（`/etc/audit/rules.d/99-custom.rules`）](#️-212-監査ルールetcauditrulesd99-customrules)
  - [🔷 22. NTP冗長化設定パラメーター](#-22-ntp冗長化設定パラメーター)
  - [🔷 23. バックアップ設定パラメーター](#-23-バックアップ設定パラメーター)
  - [🔷 24. ログ転送設定パラメーター](#-24-ログ転送設定パラメーター)
  - [🔷 25. EDR・マルウェア対策パラメーター](#-25-edrマルウェア対策パラメーター)
  - [🔷 26. 監視設定パラメーター](#-26-監視設定パラメーター)
  - [🔷 27. パッチ管理設定パラメーター](#-27-パッチ管理設定パラメーター)
  - [🔷 28. sudo設定パラメーター](#-28-sudo設定パラメーター)
  - [🔷 29. サービス自動復旧設定パラメーター](#-29-サービス自動復旧設定パラメーター)
  - [🔷 30. 運用管理サービス設定パラメーター](#-30-運用管理サービス設定パラメーター)
    - [▶️ 30.1 SSH公開鍵集中管理（FreeIPA連携）](#️-301-ssh公開鍵集中管理freeipa連携)
    - [▶️ 30.2 Ansible構成管理パラメーター](#️-302-ansible構成管理パラメーター)


---


## 🔷 1. OS基本設定パラメーター

### ▶️ 1.1 システム基本情報

| パラメーター名 | 設定ファイル・コマンド | 設定値 | 備考 |
|-------------|---------------------|--------|------|
| ホスト名 | `hostnamectl set-hostname` | ★設定値 | 例: web-prod-01.example.com |
| タイムゾーン | `timedatectl set-timezone` | Asia/Tokyo | |
| ロケール | `localectl set-locale` | LANG=ja_JP.UTF-8 | |
| キーボード | `localectl set-keymap` | jp106 | |
| OSバージョン | `/etc/os-release` | AlmaLinux 9.4 | `cat /etc/os-release` で確認 |
| カーネルバージョン | `uname -r` | 5.14.0-427.xx.x.el9.x86_64 | 確認後記載 |
| systemdバージョン | `systemctl --version` | 252 | RHEL9標準 |

### ▶️ 1.2 GRUB2 パラメーター（`/etc/default/grub`）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `GRUB_TIMEOUT` | 5 | タイムアウト（秒） |
| `GRUB_DEFAULT` | saved | デフォルト起動エントリ |
| `GRUB_DISABLE_RECOVERY` | true | 回復モードメニューを非表示 |
| `GRUB_CMDLINE_LINUX` | `quiet audit=1 selinux=1 security=selinux` | カーネルコマンドラインオプション |
| `GRUB_ENABLE_BLSCFG` | true | **RHEL9ではデフォルト true**（BLS形式） |

設定反映コマンド：
```bash
# UEFI環境
grub2-mkconfig -o /boot/efi/EFI/almalinux/grub.cfg

# BIOS環境
grub2-mkconfig -o /boot/grub2/grub.cfg

# BLSエントリの管理（推奨）
grubby --info=ALL
grubby --update-kernel=ALL --args="quiet audit=1"
```

### ▶️ 1.3 systemd 設定パラメーター

| パラメーター名 | 設定ファイル | 設定値 | 備考 |
|-------------|-----------|--------|------|
| デフォルトターゲット | `systemctl set-default` | multi-user.target | サーバー用途 |
| ジャーナル永続化 | `/etc/systemd/journald.conf` `[Journal] Storage=` | persistent | `/var/log/journal` に保存 |
| ジャーナル最大サイズ | `/etc/systemd/journald.conf` `SystemMaxUse=` | 1G | |
| ジャーナル最大ファイルサイズ | `/etc/systemd/journald.conf` `SystemMaxFileSize=` | 100M | |
| ジャーナル圧縮 | `/etc/systemd/journald.conf` `Compress=` | yes | RHEL9デフォルト |
| RateLimit（バースト） | `/etc/systemd/journald.conf` `RateLimitBurst=` | 10000 | ログ欠損防止 |

---

## 🔷 2. カーネルパラメーター（`/etc/sysctl.d/99-custom.conf`）

### ▶️ 2.1 ネットワークセキュリティ

| パラメーター名 | 推奨値 | 本番設定値 | 備考 |
|-------------|--------|---------|------|
| `net.ipv4.ip_forward` | 0 | ★設定値 | ルーターは1 |
| `net.ipv4.conf.all.send_redirects` | 0 | 0 | |
| `net.ipv4.conf.default.send_redirects` | 0 | 0 | |
| `net.ipv4.conf.all.accept_redirects` | 0 | 0 | |
| `net.ipv4.conf.default.accept_redirects` | 0 | 0 | |
| `net.ipv4.conf.all.accept_source_route` | 0 | 0 | |
| `net.ipv4.conf.all.log_martians` | 1 | 1 | 不正パケットをログ記録 |
| `net.ipv4.tcp_syncookies` | 1 | 1 | SYN Flood対策 |
| `net.ipv4.conf.all.rp_filter` | 1 | 1 | スプーフィング対策 |
| `net.ipv4.icmp_echo_ignore_broadcasts` | 1 | 1 | Smurf攻撃対策 |
| `net.ipv4.icmp_ignore_bogus_error_responses` | 1 | 1 | |
| `net.ipv4.tcp_timestamps` | 0 | 0 | タイムスタンプ無効（情報漏洩防止） |
| `net.ipv6.conf.all.disable_ipv6` | 1 | ★設定値 | IPv6不要時は1 |
| `net.ipv6.conf.default.disable_ipv6` | 1 | ★設定値 | |

### ▶️ 2.2 カーネルセキュリティ・パフォーマンス

| パラメーター名 | 推奨値 | 本番設定値 | 備考 |
|-------------|--------|---------|------|
| `kernel.sysrq` | 0 | 0 | SysRqキー無効 |
| `kernel.core_uses_pid` | 1 | 1 | コアダンプにPIDを付加 |
| `kernel.dmesg_restrict` | 1 | 1 | 一般ユーザーのdmesg制限 |
| `kernel.perf_event_paranoid` | 2 | 2 | perfイベント制限 |
| `kernel.randomize_va_space` | 2 | 2 | ASLR有効（フルランダム化） |
| `kernel.yama.ptrace_scope` | 1 | 1 | ptrace制限（RHEL9デフォルト1） |
| `fs.suid_dumpable` | 0 | 0 | SUID実行ファイルのコアダンプ禁止 |
| `fs.protected_hardlinks` | 1 | 1 | ハードリンク保護（RHEL9デフォルト） |
| `fs.protected_symlinks` | 1 | 1 | シンボリックリンク保護（RHEL9デフォルト） |
| `vm.swappiness` | 10 | ★設定値 | DBは10、一般は60 |
| `vm.dirty_ratio` | 20 | ★設定値 | ダーティページ上限（%） |
| `net.core.somaxconn` | 4096 | ★設定値 | 接続キューサイズ |
| `net.ipv4.tcp_max_syn_backlog` | 8192 | ★設定値 | SYNキューサイズ |

設定反映コマンド：
```bash
sysctl --system
# または個別ファイル
sysctl -p /etc/sysctl.d/99-custom.conf
```

---

## 🔷 3. ストレージ・ファイルシステムパラメーター

### ▶️ 3.1 パーティション構成（`/etc/fstab`）

| マウントポイント | デバイス/UUID | ファイルシステム | マウントオプション | dump | pass |
|--------------|------------|--------------|----------------|------|------|
| `/` | UUID=★設定値 | xfs | defaults | 0 | 0 |
| `/boot` | UUID=★設定値 | xfs | defaults | 0 | 0 |
| `/boot/efi` | UUID=★設定値 | vfat | umask=0077,shortname=winnt | 0 | 2 |
| `/var` | UUID=★設定値 | xfs | defaults | 0 | 0 |
| `/home` | UUID=★設定値 | xfs | defaults,nodev | 0 | 0 |
| `/tmp` | UUID=★設定値 | xfs | defaults,nodev,nosuid,noexec | 0 | 0 |
| `swap` | UUID=★設定値 | swap | defaults | 0 | 0 |

UUID確認コマンド：
```bash
blkid
lsblk -f
```

> **RHEL9注意**：`dump` フィールドは通常 0（現代のバックアップツールは fstab に依存しない）。XFSでは `pass` は 0 推奨（fsckはXFSに不要）。

---

## 🔷 4. ネットワーク設定パラメーター

### ▶️ 4.1 NIC設定（NetworkManager keyfile形式）

**設定ファイルパス**：`/etc/NetworkManager/system-connections/★接続名.nmconnection`

```ini
[connection]
id=★接続名
type=ethernet
interface-name=★デバイス名

[ethernet]

[ipv4]
method=manual
address1=★IPアドレス/★プレフィクス長,★ゲートウェイIP
dns=★DNSサーバー1;★DNSサーバー2;
dns-search=★検索ドメイン
ignore-auto-dns=true

[ipv6]
method=disabled

[proxy]
```

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `id`（接続名） | ★設定値 | 例: ens3-static |
| `interface-name` | ★設定値 | 例: ens3, enp3s0 |
| `method`（ipv4） | manual | 静的IP設定 |
| `address1` | ★IP/プレフィクス,★GW | 例: 192.168.1.10/24,192.168.1.1 |
| `dns` | ★設定値 | セミコロン区切り |
| `dns-search` | ★設定値 | 検索ドメイン |

> **重要**：`/etc/sysconfig/network-scripts/ifcfg-*` 形式は **RHEL9でdeprecated**。新規設定はkeyfile形式を使用すること。

設定コマンド例：
```bash
nmcli con add type ethernet con-name ens3-static ifname ens3 \
  ipv4.method manual \
  ipv4.addresses 192.168.1.10/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "192.168.1.53 8.8.8.8" \
  ipv6.method disabled
nmcli con up ens3-static
```

### ▶️ 4.2 `/etc/hosts`

| IPアドレス | ホスト名（FQDN） | エイリアス | 備考 |
|----------|--------------|---------|------|
| 127.0.0.1 | localhost | localhost.localdomain | |
| ::1 | localhost | localhost6.localdomain6 | IPv6 |
| ★設定値 | ★設定値（FQDN） | ★設定値（短縮名） | サーバー自身 |

### ▶️ 4.3 `/etc/resolv.conf`

> **RHEL9注意**：`/etc/resolv.conf` は NetworkManager が自動生成。手動編集は `NetworkManager.conf` の `dns=none` 設定が必要。

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| domain | ★設定値 | 例: example.com |
| search | ★設定値 | 例: example.com internal.example.com |
| nameserver 1 | ★設定値 | プライマリDNS |
| nameserver 2 | ★設定値 | セカンダリDNS |

### ▶️ 4.4 `/etc/nsswitch.conf`（名前解決順序）

| データベース | 設定値 | 備考 |
|-----------|--------|------|
| hosts | files dns | /etc/hosts → DNS の順に解決 |
| passwd | files sss | ローカル → SSSD（LDAP連携時） |
| shadow | files sss | |
| group | files sss | |

---

## 🔷 5. SSH設定パラメーター（`/etc/ssh/sshd_config`）

**前提**：OpenSSH **8.7p1**（RHEL9標準）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `Port` | ★設定値 | デフォルト22。変更推奨 |
| `AddressFamily` | inet | IPv4のみ |
| `ListenAddress` | ★設定値 | リッスンIP（0.0.0.0は全NIC） |
| `SyslogFacility` | AUTHPRIV | 認証ログファシリティ |
| `LogLevel` | VERBOSE | INFO → VERBOSEで指紋情報も記録 |
| `LoginGraceTime` | 30 | ログイン試行タイムアウト（秒） |
| `PermitRootLogin` | no | root直接ログイン禁止 |
| `StrictModes` | yes | ホームディレクトリパーミッション確認 |
| `MaxAuthTries` | 3 | 認証失敗最大回数 |
| `MaxSessions` | 5 | 最大セッション数（10から5に削減） |
| `HostKey` | /etc/ssh/ssh_host_ed25519_key | **Ed25519を優先** |
| `HostKey` | /etc/ssh/ssh_host_ecdsa_key | ECDSAを2番目 |
| `HostKey` | /etc/ssh/ssh_host_rsa_key | RSAを3番目（互換性のため） |
| `PubkeyAuthentication` | yes | 公開鍵認証有効 |
| `AuthorizedKeysFile` | .ssh/authorized_keys | 公開鍵ファイルパス |
| `PasswordAuthentication` | no | パスワード認証無効 |
| `PermitEmptyPasswords` | no | 空パスワード禁止 |
| `KbdInteractiveAuthentication` | no | チャレンジレスポンス認証無効（新パラメーター名） |
| `UsePAM` | yes | PAM連携 |
| `X11Forwarding` | no | X11フォワーディング禁止 |
| `PrintMotd` | no | MOTDをSSHで非表示 |
| `ClientAliveInterval` | 300 | アイドルチェック間隔（秒） |
| `ClientAliveCountMax` | 3 | アイドルタイムアウト回数 |
| `AllowUsers` または `AllowGroups` | ★設定値 | 許可ユーザー/グループ（どちらか一方を使用） |
| `Banner` | /etc/ssh/banner | ログインバナー（任意） |
| `Ciphers` | chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr | RHEL9 OpenSSH 8.7推奨暗号スイート |
| `MACs` | hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha2-256,hmac-sha2-512 | ETM優先 |
| `KexAlgorithms` | curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256 | curve25519優先 |
| `HostKeyAlgorithms` | ssh-ed25519,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,rsa-sha2-512,rsa-sha2-256 | Ed25519優先 |
| `PubkeyAcceptedAlgorithms` | ssh-ed25519,sk-ssh-ed25519@openssh.com,ecdsa-sha2-nistp256,rsa-sha2-512,rsa-sha2-256 | Ed25519優先 |

---

## 🔷 6. ユーザー・PAM設定パラメーター

### ▶️ 6.1 パスワードポリシー（`/etc/security/pwquality.conf`）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `minlen` | 12 | 最小パスワード長（NIST SP800-63準拠で12文字推奨） |
| `dcredit` | -1 | 数字を最低1文字含む |
| `ucredit` | -1 | 大文字を最低1文字含む |
| `lcredit` | -1 | 小文字を最低1文字含む |
| `ocredit` | -1 | 記号を最低1文字含む |
| `maxrepeat` | 3 | 同じ文字の最大連続数 |
| `maxsequence` | 3 | 連続文字（abc等）の最大長 |
| `usercheck` | 1 | ユーザー名を含むパスワードを禁止 |
| `dictcheck` | 1 | 辞書チェック有効 |
| `enforcing` | 1 | ポリシー違反を強制（エラー） |

### ▶️ 6.2 アカウントロック（`/etc/security/faillock.conf`）

> **重要**：RHEL9では `pam_tally2` は廃止済み。`pam_faillock` を使用すること。

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `deny` | 5 | 失敗回数でロック |
| `fail_interval` | 900 | 失敗カウント間隔（秒） |
| `unlock_time` | 600 | ロック解除時間（秒）。0は管理者解除のみ |
| `audit` | （記載） | 失敗をauditログに記録 |
| `silent` | （記載なし） | デフォルトは非サイレント（失敗メッセージを表示） |
| `even_deny_root` | （記載） | rootもロック対象 |
| `root_unlock_time` | 60 | rootのロック解除時間（短め） |

手動ロック解除：
```bash
faillock --user ★ユーザー名 --reset
faillock --user ★ユーザー名  # ロック状態確認
```

### ▶️ 6.3 パスワード有効期限（`/etc/login.defs`）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `PASS_MAX_DAYS` | 90 | パスワード最大有効期間（日） |
| `PASS_MIN_DAYS` | 1 | パスワード変更最小間隔（日） |
| `PASS_WARN_AGE` | 14 | 有効期限警告日数（7→14日に延長） |
| `UID_MIN` | 1000 | 一般ユーザーUID最小値 |
| `UID_MAX` | 60000 | 一般ユーザーUID最大値 |
| `CREATE_HOME` | yes | ホームディレクトリ自動作成 |
| `UMASK` | 077 | デフォルトumask |
| `ENCRYPT_METHOD` | **YESCRYPT** | **RHEL9デフォルト。SHA512より強固** |

---

## 🔷 7. DNS設定パラメーター（BIND 9.16 / named）

### ▶️ 7.1 `/etc/named.conf` 主要パラメーター

**前提**：BIND **9.16**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `listen-on port 53` | `{ 127.0.0.1; ★設定値; };` | リッスンIPアドレス |
| `listen-on-v6` | `{ none; };` | IPv6リッスン（無効） |
| `directory` | /var/named | ゾーンファイル格納ディレクトリ |
| `dump-file` | /var/named/data/cache_dump.db | キャッシュダンプ先 |
| `allow-query` | `{ localhost; ★内部NW; };` | クエリ許可元 |
| `recursion` | yes（キャッシュDNS）/ no（権威DNS） | 再帰問い合わせ設定 |
| `allow-recursion` | `{ 127.0.0.1; ★内部NW; };` | 再帰クエリ許可元（キャッシュDNSのみ） |
| `dnssec-validation` | auto | DNSSEC検証（自動） |
| `version` | `"none"` | バージョン情報非表示 |
| `notify` | yes | ゾーン変更通知有効 |
| `allow-transfer` | `{ ★セカンダリDNS-IP; };` | ゾーン転送許可先 |

### ▶️ 7.2 DNSSEC設定（BIND 9.16 `dnssec-policy`）

BIND 9.16以降は `dnssec-policy` ディレクティブで自動管理が可能：

```conf
zone "example.com" {
    type primary;
    file "example.com.zone";
    dnssec-policy default;  # KSK/ZSK自動ロールオーバー
    inline-signing yes;
};
```

### ▶️ 7.3 ゾーンファイルパラメーター（正引き）

| レコードタイプ | 設定値例 | 備考 |
|-------------|---------|------|
| `$TTL` | 86400 | デフォルトTTL（秒） |
| SOA Serial | ★YYYYMMDDnn形式 | 例: 2025061701 |
| Refresh | 3600 | セカンダリリフレッシュ間隔（秒） |
| Retry | 900 | 再試行間隔（秒） |
| Expire | 604800 | 有効期限（秒） |
| Negative TTL | 300 | 否定応答TTL（秒） |
| `NS` | ns1.example.com. | ネームサーバー |
| `MX 10` | mail.example.com. | メールサーバー |
| `A` | ★設定値 | ホスト→IPv4アドレス |
| `AAAA` | ★設定値 | ホスト→IPv6アドレス |
| `CNAME` | ★設定値 | 別名レコード |
| `TXT`（SPF） | `v=spf1 ip4:★IP -all` | SPFレコード |
| `TXT`（DMARC） | `v=DMARC1; p=quarantine; rua=mailto:★` | DMARCレコード |
| `CAA` | `0 issue "letsencrypt.org"` | 証明書認証局指定（推奨） |

---

## 🔷 8. Webサーバー設定パラメーター

### ▶️ 8.1 Apache（`/etc/httpd/conf/httpd.conf`）

**前提**：httpd **2.4.57**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `ServerName` | ★設定値 | 例: www.example.com:80 |
| `ServerRoot` | /etc/httpd | |
| `DocumentRoot` | /var/www/html | |
| `Listen` | 80 | HTTP |
| `ServerAdmin` | ★設定値 | 管理者メールアドレス |
| `ServerTokens` | Prod | バージョン情報を最小表示 |
| `ServerSignature` | Off | エラーページのサーバー情報を非表示 |
| `TraceEnable` | Off | TRACEメソッド無効 |
| `Options` | -Indexes -FollowSymLinks -ExecCGI | ディレクトリリスティング禁止 |
| `AllowOverride` | None | .htaccessを無効 |
| `KeepAlive` | On | 持続的接続有効 |
| `KeepAliveTimeout` | 5 | 持続接続タイムアウト（秒） |
| `Timeout` | 60 | リクエストタイムアウト（秒） |
| `LogLevel` | warn | ログレベル |
| `H2Direct` | on | HTTP/2 Direct（mod_http2有効時） |

### ▶️ 8.2 SSL/TLS設定（`/etc/httpd/conf.d/ssl.conf`）

**前提**：TLS 1.2 / TLS 1.3 のみ許可。SSLv2/SSLv3/TLS1.0/TLS1.1は廃止。

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `SSLEngine` | on | SSL/TLS有効 |
| `SSLProtocol` | `-All +TLSv1.2 +TLSv1.3` | **TLS1.2/1.3のみ。-All で全無効後に許可を追加** |
| `SSLCipherSuite TLSv1.3` | `TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256` | TLS1.3暗号スイート |
| `SSLCipherSuite` | `ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256` | TLS1.2暗号スイート（ECDHE優先） |
| `SSLHonorCipherOrder` | on | サーバー優先の暗号選択 |
| `SSLCertificateFile` | /etc/pki/tls/certs/★.crt | サーバー証明書 |
| `SSLCertificateKeyFile` | /etc/pki/tls/private/★.key | 秘密鍵 |
| `SSLCertificateChainFile` | /etc/pki/tls/certs/★-chain.crt | 中間証明書 |
| `SSLCompression` | off | SSL圧縮無効（CRIME攻撃対策） |
| `SSLSessionTickets` | off | セッションチケット無効（PFS確保） |
| `Header always set Strict-Transport-Security` | "max-age=63072000; includeSubDomains; preload" | HSTS（2年） |
| `Header always set X-Frame-Options` | DENY | クリックジャッキング対策 |
| `Header always set X-Content-Type-Options` | nosniff | MIMEスニッフィング防止 |
| `Header always set Referrer-Policy` | strict-origin-when-cross-origin | リファラーポリシー |
| `Header always set Permissions-Policy` | "geolocation=(), microphone=(), camera=()" | 機能ポリシー |

### ▶️ 8.3 Nginx（`/etc/nginx/nginx.conf`）

**前提**：Nginx **1.22**（RHEL9 AppStream）またはNginx 1.24（mainline）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `worker_processes` | auto | CPUコア数自動 |
| `worker_connections` | 1024 | ワーカー最大接続数 |
| `keepalive_timeout` | 65 | Keep-Aliveタイムアウト（秒） |
| `server_tokens` | off | バージョン情報非表示 |
| `client_max_body_size` | 10m | 最大リクエストボディサイズ |
| `gzip` | on | gzip圧縮有効 |
| `gzip_types` | text/plain text/css application/json application/javascript text/xml | 圧縮対象 |
| `ssl_protocols` | TLSv1.2 TLSv1.3 | TLS1.2/1.3のみ |
| `ssl_ciphers` | ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305 | モダン暗号スイート |
| `ssl_prefer_server_ciphers` | off | TLS1.3ではクライアント優先が推奨 |
| `ssl_session_cache` | shared:SSL:10m | SSLセッションキャッシュ |
| `ssl_session_timeout` | 1d | セッションタイムアウト |
| `ssl_session_tickets` | off | セッションチケット無効（PFS確保） |
| `ssl_certificate` | /etc/nginx/ssl/★.crt | 証明書パス |
| `ssl_certificate_key` | /etc/nginx/ssl/★.key | 秘密鍵パス |
| `ssl_stapling` | on | OCSPステープリング有効 |
| `ssl_stapling_verify` | on | OCSPステープリング検証 |
| `http2` | on | HTTP/2有効（Nginx 1.25.1以降は `listen 443 ssl`の後に追記） |
| `access_log` | /var/log/nginx/access.log main | アクセスログ |
| `error_log` | /var/log/nginx/error.log warn | エラーログ |

---

## 🔷 9. ファイル共有設定パラメーター

### ▶️ 9.1 Samba（`/etc/samba/smb.conf`）- [global]セクション

**前提**：Samba **4.17**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `workgroup` | ★設定値 | ワークグループ名（例: WORKGROUP） |
| `server string` | ★設定値 | サーバー説明文 |
| `netbios name` | ★設定値 | NetBIOS名 |
| `security` | user | 認証方式（ADS: AD統合時） |
| `log file` | /var/log/samba/log.%m | ログファイル |
| `max log size` | 1000 | 最大ログサイズ（KB） |
| `ntlm auth` | **ntlmv2-only** | **NTLMv1廃止。ntlmv2-onlyを指定** |
| `server min protocol` | **SMB2** | **SMB1は廃止済み・デフォルト無効** |
| `server max protocol` | SMB3 | 最高プロトコルバージョン |
| `smb encrypt` | desired | 暗号化推奨（required: 必須） |
| `unix charset` | UTF-8 | 文字コード |
| `log level` | 1 | ログ詳細レベル |

### ▶️ 9.2 Samba 共有定義（[share]セクション）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `comment` | ★設定値 | 共有の説明 |
| `path` | ★設定値 | 共有ディレクトリパス |
| `browsable` | yes / no | ブラウズ表示 |
| `writable` | yes / no | 書き込み許可 |
| `valid users` | ★設定値 | アクセス許可ユーザー/グループ（@グループ名） |
| `create mask` | 0664 | 作成ファイルのパーミッション |
| `directory mask` | 0775 | 作成ディレクトリのパーミッション |
| `force group` | ★設定値 | 強制グループ |

### ▶️ 9.3 NFS（`/etc/nfs.conf` + `/etc/exports`）

**前提**：NFS **v4.2**（RHEL9標準。NFSv2/v3は非推奨）

**`/etc/nfs.conf`（RHEL9の新設定ファイル）：**

```ini
[nfsd]
vers2=n         # NFSv2無効
vers3=n         # NFSv3無効（推奨）
vers4=y
vers4.1=y
vers4.2=y       # NFSv4.2有効（最新）
```

**`/etc/exports`：**

| エクスポートパス | 許可クライアント | オプション | 備考 |
|--------------|--------------|---------|------|
| /export/share | ★IP/CIDR | rw,sync,no_subtree_check,root_squash,sec=krb5p | NFSv4.2 + Kerberos推奨 |
| /export/readonly | ★IP/CIDR | ro,sync,no_subtree_check,root_squash | 読み取り専用 |

設定反映：
```bash
exportfs -ra
systemctl restart nfs-server
```

---

## 🔷 10. メールサービス設定パラメーター

### ▶️ 10.1 Postfix（`/etc/postfix/main.cf`）

**前提**：Postfix **3.5.9**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `myhostname` | ★設定値 | メールサーバーのFQDN（例: mail.example.com） |
| `mydomain` | ★設定値 | ドメイン名（例: example.com） |
| `myorigin` | $mydomain | 送信メールのドメイン |
| `inet_interfaces` | all | リッスンIF（送信専用は loopback-only） |
| `inet_protocols` | ipv4 | 使用プロトコル（IPv6使用時はall） |
| `mydestination` | $myhostname, localhost.$mydomain, $mydomain | ローカル配送対象 |
| `relayhost` | ★設定値 | リレー先（空白=直接配送） |
| `mynetworks` | 127.0.0.0/8 ★内部NW | SMTP中継許可ネットワーク |
| `home_mailbox` | Maildir/ | Maildir形式 |
| `smtpd_banner` | $myhostname ESMTP | バナー（バージョン非表示） |
| `smtpd_tls_security_level` | **encrypt** | **STARTTLS必須（may→encryptに強化）** |
| `smtp_tls_security_level` | may | 送信側TLS（可能なら使用） |
| `smtpd_tls_cert_file` | /etc/pki/tls/certs/★.crt | TLS証明書 |
| `smtpd_tls_key_file` | /etc/pki/tls/private/★.key | TLS秘密鍵 |
| `smtpd_tls_protocols` | `!SSLv2, !SSLv3, !TLSv1, !TLSv1.1` | TLS1.2/1.3のみ許可 |
| `smtpd_tls_mandatory_protocols` | `!SSLv2, !SSLv3, !TLSv1, !TLSv1.1` | 必須TLSバージョン |
| `smtpd_tls_ciphers` | high | 強い暗号スイートのみ |
| `smtpd_sasl_auth_enable` | yes | SASL認証有効 |
| `smtpd_sasl_security_options` | noanonymous | 匿名SASL禁止 |
| `smtpd_recipient_restrictions` | permit_mynetworks, permit_sasl_authenticated, reject_unauth_destination | 受信制限 |
| `smtpd_helo_required` | yes | HELOコマンド必須 |
| `disable_vrfy_command` | yes | VRFYコマンド無効（ユーザー列挙防止） |
| `message_size_limit` | 10240000 | 最大10MB |
| `mailbox_size_limit` | 51200000 | 最大50MB |

### ▶️ 10.2 Dovecot（`/etc/dovecot/dovecot.conf`）

**前提**：Dovecot **2.3.16**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `protocols` | imap pop3 lmtp | 有効プロトコル（平文は有効化しない） |
| `listen` | ★設定値 | リッスンIP |
| `ssl` | required | SSL必須 |
| `ssl_cert` | </etc/pki/dovecot/certs/★.crt | SSL証明書 |
| `ssl_key` | </etc/pki/dovecot/private/★.key | SSL秘密鍵 |
| `ssl_min_protocol` | **TLSv1.2** | TLS1.2以上のみ |
| `ssl_cipher_list` | ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:... | モダン暗号スイート |
| `ssl_prefer_server_ciphers` | yes | サーバー優先 |
| `mail_location` | maildir:~/Maildir | メールボックス場所 |
| `auth_mechanisms` | plain login | TLS経由のみ（平文は禁止しない、TLS必須で保護） |
| `disable_plaintext_auth` | yes | 非TLS時の平文認証禁止 |

---

## 🔷 11. DHCPサービス設定パラメーター（`/etc/dhcp/dhcpd.conf`）

**前提**：ISC DHCP **4.4.2**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `default-lease-time` | 86400 | デフォルトリース時間（秒）= 24時間 |
| `max-lease-time` | 604800 | 最大リース時間（秒）= 7日 |
| `option domain-name` | "★設定値" | ドメイン名 |
| `option domain-name-servers` | ★DNSサーバーIP | DNSサーバー |
| `option routers` | ★ゲートウェイIP | デフォルトゲートウェイ |
| `option subnet-mask` | ★設定値 | サブネットマスク |
| subnet（定義） | ★ネットワークアドレス | 例: 192.168.1.0 netmask 255.255.255.0 |
| range（IPプール） | ★開始IP ～ ★終了IP | 動的割当範囲 |
| host（固定割当） | hardware ethernet ★MAC; fixed-address ★IP; | 特定機器への固定IP |
| `ddns-update-style` | none | 動的DNS更新 |
| `authoritative` | （記載） | 権威DHCPであることを宣言 |
| `log-facility` | local7 | syslogファシリティ |

---

## 🔷 12. FTPサービス設定パラメーター（`/etc/vsftpd/vsftpd.conf`）

**前提**：vsftpd **3.0.5**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `anonymous_enable` | NO | 匿名アクセス禁止 |
| `local_enable` | YES | ローカルユーザーのログイン許可 |
| `write_enable` | YES / NO | 書き込み許可 |
| `local_umask` | 022 | アップロードファイルのumask |
| `chroot_local_user` | YES | ローカルユーザーのchroot有効 |
| `chroot_list_enable` | YES | chroot除外リストを有効 |
| `chroot_list_file` | /etc/vsftpd/chroot_list | chroot除外ユーザーリスト |
| `allow_writeable_chroot` | YES | chroot内の書き込み許可（必要な場合） |
| `ssl_enable` | YES | SSL/TLS有効 |
| `ssl_tlsv1_2` | YES | TLS 1.2有効 |
| `ssl_sslv2` | NO | SSLv2無効 |
| `ssl_sslv3` | NO | SSLv3無効 |
| `ssl_tlsv1` | NO | TLS1.0無効 |
| `rsa_cert_file` | /etc/pki/tls/certs/★.crt | 証明書 |
| `rsa_private_key_file` | /etc/pki/tls/private/★.key | 秘密鍵 |
| `force_local_logins_ssl` | YES | ローカルユーザーはSSL必須 |
| `force_local_data_ssl` | YES | データ転送もSSL必須 |
| `pasv_enable` | YES | パッシブモード有効 |
| `pasv_min_port` | ★設定値 | パッシブポート範囲（開始） |
| `pasv_max_port` | ★設定値 | パッシブポート範囲（終了） |
| `listen` | YES | スタンドアロンモード（IPv4） |
| `listen_ipv6` | NO | IPv6リッスン無効 |
| `userlist_enable` | YES | 許可ユーザーリスト有効 |
| `userlist_file` | /etc/vsftpd/user_list | 許可ユーザーリスト |
| `userlist_deny` | NO | リストのユーザーのみ許可 |
| `tcp_wrappers` | NO | **RHEL9ではtcp_wrappersは廃止** |
| `max_clients` | ★設定値 | 最大クライアント数 |
| `max_per_ip` | ★設定値 | 同一IPからの最大接続数 |
| `xferlog_enable` | YES | 転送ログ有効 |
| `xferlog_std_format` | YES | wu-ftpd互換ログ形式 |

---

## 🔷 13. OpenVPN設定パラメーター（`/etc/openvpn/server/server.conf`）

**前提**：OpenVPN **2.5.9**（EPEL経由）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `port` | 1194 | VPNポート |
| `proto` | udp | プロトコル（udp推奨） |
| `dev` | tun | インターフェース |
| `ca` | /etc/openvpn/server/pki/ca.crt | CA証明書 |
| `cert` | /etc/openvpn/server/pki/issued/server.crt | サーバー証明書 |
| `key` | /etc/openvpn/server/pki/private/server.key | サーバー秘密鍵 |
| `dh` | **none** | **ECDH使用（DH鍵ファイル廃止推奨）** |
| `ecdh-curve` | prime256v1 | ECDHカーブ |
| `tls-crypt` | /etc/openvpn/server/ta.key | **双方向TLS認証（tls-authより安全）** |
| `tls-version-min` | 1.2 | 最低TLSバージョン |
| `tls-cipher` | TLS-ECDHE-ECDSA-WITH-AES-256-GCM-SHA384:TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384 | TLS暗号スイート |
| `server` | ★設定値 255.255.255.0 | VPNサブネット |
| `push "route"` | ★設定値 | クライアントへのルート配布 |
| `push "dhcp-option DNS"` | ★DNSサーバーIP | クライアントへのDNS配布 |
| `ifconfig-pool-persist` | /etc/openvpn/server/ipp.txt | IPプール永続化 |
| `keepalive` | 10 120 | Keepalive設定 |
| `cipher` | AES-256-GCM | データ暗号化アルゴリズム |
| `data-ciphers` | AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305 | 許可暗号リスト（2.5以降） |
| `auth` | SHA256 | HMAC認証 |
| `user` | nobody | 実行ユーザー |
| `group` | nobody | 実行グループ |
| `persist-key` | （記載） | 鍵を再読み込みしない |
| `persist-tun` | （記載） | TUNデバイスを再作成しない |
| `status` | /var/log/openvpn/openvpn-status.log | ステータスログ |
| `log-append` | /var/log/openvpn/openvpn.log | 接続ログ |
| `verb` | 3 | ログ詳細レベル |
| `explicit-exit-notify` | 1 | クライアント切断時に通知 |

---

## 🔷 14. セキュリティ設定パラメーター

### ▶️ 14.1 SELinux（`/etc/selinux/config`）

**前提**：SELinux **3.5**（RHEL9標準）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `SELINUX` | enforcing | enforcing: 強制 / permissive: 警告のみ |
| `SELINUXTYPE` | targeted | targeted: 主要サービス対象 |

```bash
# 現在の状態確認
getenforce
sestatus

# ブール値の永続変更
setsebool -P httpd_can_network_connect on

# ラベルの永続変更
semanage fcontext -a -t httpd_sys_content_t "/webdata(/.*)?"
restorecon -Rv /webdata
```

### ▶️ 14.2 firewalld 許可サービス一覧

**前提**：firewalld **1.2**（バックエンド：nftables **1.0.4**）

> **重要**：RHEL9では `iptables` コマンドは nftables のレガシーラッパー。`firewall-cmd` で統一管理すること。

| サービス名 | プロトコル | ポート | ゾーン | 有効/無効 |
|---------|----------|------|--------|---------|
| ssh | TCP | 22 | internal | 有効 |
| http | TCP | 80 | public | ★設定値 |
| https | TCP | 443 | public | ★設定値 |
| dns | TCP/UDP | 53 | internal | ★設定値 |
| smtp | TCP | 25 | internal | ★設定値 |
| smtps | TCP | 465 | internal | ★設定値 |
| pop3s | TCP | 995 | internal | ★設定値 |
| imaps | TCP | 993 | internal | ★設定値 |
| ftp | TCP | 21 | internal | ★設定値 |
| ftp-data | TCP | 20 | internal | ★設定値 |
| nfs | TCP | 2049 | internal | ★設定値 |
| samba | TCP | 445 | internal | ★設定値 |
| dhcp | UDP | 67 | internal | ★設定値 |
| openvpn | UDP | 1194 | public | ★設定値 |
| ntp | UDP | 123 | internal | ★設定値 |
| squid | TCP | 3128 | internal | ★設定値 |

```bash
# サービス追加例（永続化）
firewall-cmd --zone=public --add-service=https --permanent
firewall-cmd --reload

# カスタムポート追加例
firewall-cmd --zone=internal --add-port=★ポート/tcp --permanent
firewall-cmd --reload
```

---

## 🔷 15. プロキシ設定パラメーター（`/etc/squid/squid.conf`）

**前提**：Squid **5.5**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `http_port` | 3128 | HTTPプロキシポート |
| `https_port` | 3129 ssl-bump cert=★ | HTTPS（SSLバンプ）ポート |
| `acl localnet src` | ★内部ネットワーク/CIDR | 許可クライアントACL |
| `acl SSL_ports port` | 443 | SSLポートACL |
| `acl Safe_ports port` | 80 21 443 70 210 1025-65535 | 安全ポートACL |
| `http_access allow localnet` | （記載） | 内部NWからのアクセス許可 |
| `http_access deny all` | （記載） | それ以外を拒否 |
| `acl blocked_urls dstdomain` | /etc/squid/blocked_urls.txt | ブロックURLリスト |
| `http_access deny blocked_urls` | （記載） | ブロックURLを拒否 |
| `cache_dir ufs` | /var/spool/squid 5000 16 256 | キャッシュ設定（5GB） |
| `maximum_object_size` | 100 MB | キャッシュ最大オブジェクトサイズ |
| `cache_mem` | 256 MB | メモリキャッシュサイズ |
| `access_log` | daemon:/var/log/squid/access.log squid | アクセスログ（daemon形式） |
| `cache_log` | /var/log/squid/cache.log | キャッシュログ |
| `via` | off | **Viaヘッダー非送信（プロキシ存在を隠蔽）** |
| `forwarded_for` | delete | X-Forwarded-Forヘッダー非送信 |
| `request_header_access X-Forwarded-For deny all` | （記載） | X-Forwarded-Forを完全削除 |

---

## 🔷 16. NTP設定パラメーター（`/etc/chrony.conf`）

**前提**：chrony **4.3**（RHEL9標準。ntpdは廃止済み）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `pool` | ntp.nict.jp iburst | 公開NTPプール（日本）。複数設定推奨 |
| `server` | ★内部NTPサーバー iburst prefer | 内部NTPサーバー指定 |
| `driftfile` | /var/lib/chrony/drift | 時刻ドリフトファイル |
| `makestep` | 1.0 3 | 起動時の時刻補正しきい値（1秒超ならstep補正、3回まで） |
| `rtcsync` | （記載） | ハードウェアクロックと同期 |
| `allow` | ★内部ネットワーク/CIDR | NTPクライアントへの時刻配布許可 |
| `local stratum` | 10 | 上位サーバー不達時のローカル層 |
| `keyfile` | /etc/chrony.keys | NTP認証鍵ファイル |
| `ntsdumpdir` | /var/lib/chrony | NTS（Network Time Security）ダンプ |
| `logdir` | /var/log/chrony | ログディレクトリ |
| `log` | tracking measurements statistics | ログ対象 |
| `leapsectz` | right/UTC | うるう秒タイムゾーン |

確認コマンド：
```bash
chronyc tracking
chronyc sources -v
chronyc sourcestats
```

---

## 🔷 17. ファイル整合性監視パラメーター（`/etc/aide.conf`）

**前提**：AIDE **0.16**（RHEL9 AppStream）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `database_in` | file:@@{DBDIR}/aide.db | 参照データベースパス |
| `database_out` | file:@@{DBDIR}/aide.db.new | 新規データベースパス |
| `gzip_dbout` | yes | データベースをgzip圧縮 |
| `report_url` | file:@@{LOGDIR}/aide.log | レポート出力先 |
| 監視ルール（NORMAL） | p+i+n+u+g+s+m+S+acl+xattrs+**sha512** | sha256→sha512に強化 |
| 監視対象ディレクトリ | /etc /bin /sbin /usr/bin /usr/sbin /boot /lib /lib64 | 重要ディレクトリ |
| 除外ディレクトリ | /var/log /tmp /proc /sys /run /dev | 変動の多いディレクトリを除外 |

初期構築・運用コマンド：
```bash
# 初期データベース作成
aide --init
mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# 整合性チェック
aide --check
```

systemd timerでの定期チェック（`/etc/systemd/system/aide-check.timer`）：
```ini
[Timer]
OnCalendar=*-*-* 04:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 🔷 18. Fail2ban設定パラメーター（`/etc/fail2ban/jail.d/custom.conf`）

**前提**：Fail2ban **1.0**（EPEL経由）

> **RHEL9注意**：`/etc/fail2ban/jail.conf` は直接編集せず、`/etc/fail2ban/jail.d/` 配下にカスタムファイルを作成すること。

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| [DEFAULT] `bantime` | 3600 | ブロック時間（秒）= 1時間 |
| [DEFAULT] `findtime` | 600 | 失敗カウント期間（秒） |
| [DEFAULT] `maxretry` | 5 | 最大失敗回数 |
| [DEFAULT] `backend` | **systemd** | **RHEL9ではsystemdバックエンドを指定** |
| [DEFAULT] `banaction` | firewallcmd-rich-rules | **firewalldと連携（ipsetより安定）** |
| [DEFAULT] `banaction_allports` | firewallcmd-rich-rules | 全ポートブロック |
| [sshd] `enabled` | true | SSH監視有効 |
| [sshd] `port` | ssh | 監視ポート |
| [sshd] `filter` | sshd | フィルタ名 |
| [sshd] `maxretry` | 3 | SSH失敗最大回数 |
| [sshd] `bantime` | 86400 | SSHブロック時間（24時間） |
| [sshd] `logpath` | %(sshd_log)s | **systemdバックエンドでは自動取得** |
| [httpd-auth] `enabled` | true（認証サイトがある場合） | Webサーバー認証エラー監視 |
| [vsftpd] `enabled` | true（FTP利用時） | FTP失敗監視 |
| `ignoreip` | 127.0.0.1/8 ::1 ★管理IPアドレス | ブロック除外IP |

確認コマンド：
```bash
fail2ban-client status
fail2ban-client status sshd
fail2ban-client unban ★IPアドレス
```

---

## 🔷 19. ディレクトリサービス設定パラメーター

> **重要**：**OpenLDAP（slapd）はRHEL9で非サポート**。FreeIPA または 389-ds（Directory Server）を使用すること。

### ▶️ 19.1 FreeIPA（`ipa` コマンドで管理）

**前提**：FreeIPA **4.10**（RHEL9 AppStream）

| 項目 | 設定値 | 備考 |
|------|--------|------|
| インストールコマンド | `ipa-server-install` | 対話型インストール |
| ドメイン | ★設定値 | 例: ipa.example.com |
| レルム（Kerberos） | ★設定値（大文字） | 例: IPA.EXAMPLE.COM |
| DNSフォワーダー | ★設定値 | 外部DNSサーバーIP |
| CA | FreeIPA自己CA（推奨）または外部CA | |
| 管理ポート | 443（HTTPS）、389（LDAP）、636（LDAPS）、88（Kerberos） | |

```bash
# FreeIPAサーバーインストール
dnf install ipa-server ipa-server-dns
ipa-server-install \
  --domain=★ドメイン \
  --realm=★レルム \
  --ds-password=★DSパスワード \
  --admin-password=★管理者パスワード \
  --mkhomedir \
  --no-ntp

# クライアントの登録
ipa-client-install --domain=★ドメイン --server=★IPAサーバー
```

### ▶️ 19.2 SSSD（`/etc/sssd/sssd.conf`）

**前提**：SSSD **2.8**（RHEL9標準）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| [sssd] `domains` | ★設定値 | 管理ドメイン名 |
| [sssd] `services` | nss, pam, ifp | RHEL9では `ifp`（InfoPipe）も追加推奨 |
| [domain/★] `id_provider` | ipa / ad / ldap | IDプロバイダー種別 |
| [domain/★] `auth_provider` | ipa / ad / krb5 | 認証プロバイダー種別 |
| [domain/★] `access_provider` | ipa / permit | アクセス制御 |
| `ipa_domain` | ★設定値 | FreeIPAドメイン（ipaプロバイダー時） |
| `ipa_server` | ★設定値 | FreeIPAサーバーFQDN |
| `cache_credentials` | true | 認証情報キャッシュ（オフライン認証） |
| `enumerate` | false | ユーザー列挙禁止（セキュリティ） |
| `ldap_id_use_start_tls` | true | STARTTLS使用（ldapプロバイダー時） |
| `krb5_ccachedir` | /tmp | Kerberosチケットキャッシュディレクトリ |

---

## 🔷 20. ログ・ジョブスケジューラー設定パラメーター

### ▶️ 20.1 rsyslog（`/etc/rsyslog.conf`）

**前提**：rsyslog **8.2102**（RHEL9標準）  
**重要**：RHEL9ではjournaldが一次ログ収集を担い、rsyslogはjournaldから転送を受ける構成が標準。

```conf
# journaldからの転送（RHEL9推奨構成）
module(load="imjournal"
       StateFile="imjournal.state"
       IgnorePreviousMsgs="on")
```

| ファシリティ・プライオリティ | 出力先 | 備考 |
|--------------------------|-------|------|
| `*.info;mail.none;authpriv.none;cron.none` | /var/log/messages | 一般システムメッセージ |
| `authpriv.*` | /var/log/secure | 認証関連ログ |
| `mail.*` | -/var/log/maillog | メールログ（非同期書き込み） |
| `cron.*` | /var/log/cron | cronログ |
| `*.emerg` | :omusrmsg:* | 緊急エラーを全ユーザー通知（RHEL9形式） |
| `kern.*` | /var/log/kern.log | カーネルログ |
| `local7.*` | /var/log/boot.log | ブートログ |
| リモート転送（任意） | `action(type="omfwd" target="★syslogサーバーIP" port="514" protocol="tcp")` | TCP転送（RHEL9 RainerScript形式） |

### ▶️ 20.2 logrotate（`/etc/logrotate.d/`）

| 設定項目 | 設定値 | 備考 |
|---------|--------|------|
| `rotate` | 7 | ローテーション世代数 |
| 頻度 | daily | 日次ローテーション |
| `compress` | compress | 圧縮有効 |
| `delaycompress` | delaycompress | 1世代目は圧縮しない |
| `missingok` | missingok | ファイルがなくてもエラーにしない |
| `notifempty` | notifempty | 空ファイルはローテーションしない |
| `sharedscripts` | sharedscripts | postrotateスクリプトを1回のみ実行 |
| `postrotate` | `/bin/systemctl kill -s HUP rsyslog.service >/dev/null 2>&1 || true` | rsyslog再読込（RHEL9形式） |

### ▶️ 20.3 ジョブスケジューラー設定

**RHEL9ではsystemd timerを優先推奨。cronと共存可能。**

**systemd timerによる定期ジョブ例**（`/etc/systemd/system/`）：

```ini
# /etc/systemd/system/security-update.timer
[Unit]
Description=Daily security update

[Timer]
OnCalendar=*-*-* 02:00:00
RandomizedDelaySec=1800
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/security-update.service
[Unit]
Description=DNF security update

[Service]
Type=oneshot
ExecStart=/usr/bin/dnf update -y --security
```

**cronによる定期ジョブ（`/etc/cron.d/`）**：

| 実行スケジュール | コマンド | 目的 | 設定ファイル |
|--------------|---------|------|------------|
| `0 2 * * *` | `dnf update -y --security` | セキュリティパッチ自動適用（**yum→dnf**） | /etc/cron.d/security-update |
| `0 3 * * *` | `/usr/sbin/aide --check 2>&1 \| mail -s 'AIDE' ★` | ファイル整合性チェック | /etc/cron.d/aide-check |
| `0 4 * * 0` | `full_backup.sh` | 週次フルバックアップ | /etc/cron.d/backup |
| `0 4 * * 1-6` | `diff_backup.sh` | 差分バックアップ | /etc/cron.d/backup |
| `*/5 * * * *` | `check_services.sh` | サービス死活監視 | /etc/cron.d/monitor |

---

## 🔷 21. 監査（auditd）設定パラメーター

**前提**：audit **3.0.7**（RHEL9標準）

### ▶️ 21.1 auditd設定（`/etc/audit/auditd.conf`）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `log_file` | /var/log/audit/audit.log | 監査ログパス |
| `log_format` | ENRICHED | **RHEL9推奨。uid/gidをユーザー名に変換** |
| `max_log_file` | 50 | 最大ログファイルサイズ（MB） |
| `max_log_file_action` | ROTATE | サイズ超過時にローテーション |
| `num_logs` | 10 | ローテーション世代数（50MB×10 = 500MB確保） |
| `space_left` | 100 | 残量警告閾値（MB） |
| `space_left_action` | SYSLOG | 残量不足時のアクション |
| `admin_space_left` | 50 | 管理者警告閾値（MB） |
| `admin_space_left_action` | SUSPEND | **監査ログ停止防止（ディスク枯渇時）** |
| `disk_full_action` | SUSPEND | ディスク満杯時のアクション |
| `disk_error_action` | SUSPEND | ディスクエラー時のアクション |
| `name_format` | HOSTNAME | ログにホスト名を付与 |
| `tcp_listen_port` | （設定しない） | リモート受信は audisp-remote で対応 |

確認コマンド：
```bash
systemctl status auditd
auditctl -l         # 有効なルール一覧
ausearch -k passwd_changes  # キーで検索
aureport --summary  # サマリーレポート
```

### ▶️ 21.2 監査ルール（`/etc/audit/rules.d/99-custom.rules`）

```
# --- バッファサイズ設定 ---
-b 8192

# --- ユーザー・グループ・認証関連 ---
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/group -p wa -k group_changes
-w /etc/gshadow -p wa -k gshadow_changes
-w /etc/security/opasswd -p wa -k passwd_changes

# --- sudo / 特権昇格 ---
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/sudoers.d/ -p wa -k sudo_changes

# --- SSH設定 ---
-w /etc/ssh/sshd_config -p wa -k sshd_config

# --- SELinux設定 ---
-w /etc/selinux/ -p wa -k selinux_changes

# --- rootコマンド実行（64bit） ---
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_exec
-a always,exit -F arch=b32 -S execve -F euid=0 -k root_exec

# --- 特権昇格（setuid/setgid） ---
-a always,exit -F arch=b64 -S setuid -S setgid -k privilege_escalation
-a always,exit -F arch=b32 -S setuid -S setgid -k privilege_escalation

# --- ファイルシステムマウント ---
-a always,exit -F arch=b64 -S mount -S umount2 -k mount_ops
-a always,exit -F arch=b32 -S mount -S umount2 -k mount_ops

# --- ネットワーク設定変更 ---
-w /etc/NetworkManager/ -p wa -k network_config
-w /etc/sysconfig/network-scripts/ -p wa -k network_config

# --- カーネルモジュール ---
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules

# --- ルールを不変に設定（変更にはrebootが必要） ---
-e 2
```

---

## 🔷 22. NTP冗長化設定パラメーター

**前提**：chrony **4.3**（RHEL9標準。ntpdは廃止済み）

**設定ファイル**：`/etc/chrony.conf`

```conf
# 内部NTPサーバー（冗長化：3台以上推奨）
server ntp1.example.local iburst prefer
server ntp2.example.local iburst
server ntp3.example.local iburst

# フォールバック：外部NTP（NICT公開NTP）
pool ntp.nict.jp iburst

# 時刻ドリフトファイル
driftfile /var/lib/chrony/drift

# 起動時の時刻補正（1秒超ならstep補正、最大3回）
makestep 1.0 3

# ハードウェアクロック同期
rtcsync

# NTPクライアントへの時刻配布許可（内部NTPサーバーの場合）
# allow ★内部ネットワーク/CIDR

# 上位NTP不達時のローカル層
local stratum 10

# NTS（Network Time Security）設定
ntsdumpdir /var/lib/chrony

# ログ設定
logdir /var/log/chrony
log tracking measurements statistics

# うるう秒タイムゾーン
leapsectz right/UTC
```

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| 内部NTPサーバー1 | ntp1.example.local iburst prefer | メインサーバー（prefer指定） |
| 内部NTPサーバー2 | ntp2.example.local iburst | セカンダリ |
| 内部NTPサーバー3 | ntp3.example.local iburst | サード |
| 外部フォールバック | ntp.nict.jp iburst | NICT公開NTP |
| `makestep` | 1.0 3 | 起動時の急速補正設定 |
| `local stratum` | 10 | 外部不達時のローカル層 |
| NTPサーバー監視 | chronyd.service の死活監視必須 | systemd + 監視ツール |

確認コマンド：
```bash
chronyc tracking       # 現在の同期状態
chronyc sources -v     # 同期元サーバー一覧
chronyc sourcestats    # 統計情報
timedatectl show       # システム時刻状態
```

---

## 🔷 23. バックアップ設定パラメーター

| 項目 | 設定値 | 備考 |
|------|--------|------|
| OSバックアップ方式 | スナップショット（VM環境） / Clonezilla（物理環境） | 仮想環境はハイパーバイザーのスナップショット機能を活用 |
| DBバックアップコマンド | `mysqldump` / `pg_dump` / `xtrabackup` | DBエンジンに応じて選択 |
| ファイルバックアップコマンド | `rsync -avz --delete` | 増分同期 |
| バックアップ先 | ★設定値（NASまたはS3互換ストレージ） | オフサイト推奨 |
| 日次バックアップ実行時刻 | 02:00（深夜帯） | 業務負荷が低い時間帯 |
| 週次フルバックアップ実行時刻 | 日曜 03:00 | |
| 保管期間（日次） | 7世代 | GFS方式 |
| 保管期間（週次） | 4世代 | GFS方式 |
| 保管期間（月次） | 12世代 | GFS方式 |
| リストア試験頻度 | 半年ごと | RTO/RPO達成確認 |
| バックアップ監視 | 成否をsyslog + 監視ツールで記録 | 失敗時アラート必須 |

**バックアップスクリプト例（`/usr/local/bin/daily_backup.sh`）：**

```bash
#!/bin/bash
BACKUP_DIR="/mnt/backup/$(date +%Y%m%d)"
LOG="/var/log/backup.log"

mkdir -p "${BACKUP_DIR}"

# ファイルバックアップ
rsync -avz --delete /var/www/ "${BACKUP_DIR}/www/" >> "${LOG}" 2>&1

# DBバックアップ（MySQL例）
mysqldump --all-databases | gzip > "${BACKUP_DIR}/db_all_$(date +%H%M).sql.gz" 2>> "${LOG}"

echo "$(date): backup completed" >> "${LOG}"
```

**systemd timerによるバックアップスケジュール（`/etc/systemd/system/daily-backup.timer`）：**

```ini
[Timer]
OnCalendar=*-*-* 02:00:00
RandomizedDelaySec=600
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 🔷 24. ログ転送設定パラメーター

**前提**：rsyslog **8.2102**（RHEL9標準）+ TLS転送設定

**設定ファイル**：`/etc/rsyslog.d/99-remote-forward.conf`

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| 転送先ホスト | ★Syslogサーバーのホスト名/IP | |
| 転送ポート | 6514 | RFC 5425 TLS syslog標準ポート |
| プロトコル | TCP | UDP不使用（信頼性確保） |
| 暗号化 | TLS（gtlsドライバー） | 平文転送禁止 |
| CA証明書 | /etc/pki/tls/certs/syslog-ca.crt | 転送先CA証明書 |
| 転送対象 | authpriv.* / kern.* / *.warning以上 | 監査・セキュリティ関連を優先 |

**設定ファイル例（`/etc/rsyslog.d/99-remote-forward.conf`）：**

```conf
# TLSモジュールのロード
module(load="omfwd")
global(DefaultNetstreamDriver="gtls"
       DefaultNetstreamDriverCAFile="/etc/pki/tls/certs/syslog-ca.crt"
       DefaultNetstreamDriverCertFile="/etc/pki/tls/certs/★サーバー証明書.crt"
       DefaultNetstreamDriverKeyFile="/etc/pki/tls/private/★サーバー秘密鍵.key")

# 認証・セキュリティログの転送
authpriv.* action(type="omfwd"
                  target="★syslogサーバーIP"
                  port="6514"
                  protocol="tcp"
                  StreamDriver="gtls"
                  StreamDriverMode="1"
                  StreamDriverAuthMode="x509/name")

# 全警告以上のログ転送
*.warning action(type="omfwd"
                 target="★syslogサーバーIP"
                 port="6514"
                 protocol="tcp"
                 StreamDriver="gtls"
                 StreamDriverMode="1"
                 StreamDriverAuthMode="x509/name")
```

---

## 🔷 25. EDR・マルウェア対策パラメーター

| 項目 | 設定値 | 備考 |
|------|--------|------|
| EDR製品 | ★設定値（CrowdStrike Falcon / SentinelOne等） | プロジェクトで選定 |
| エージェントパス | ★製品依存 | 製品ドキュメント参照 |
| マルウェアスキャン | リアルタイム有効 | ファイル作成・変更時に自動スキャン |
| 定義ファイル更新 | 自動（日次以上） | 手動更新は緊急時のみ |
| スキャン除外ディレクトリ | /proc /sys /dev /var/lib/mysql（DB用途時） | パフォーマンス・誤検知防止 |
| アラート通知 | EDRコンソール + Syslog転送 | SIEM連携 |
| エージェント死活監視 | systemd + 監視ツール | エージェント停止を検知 |

**ClamAV設定パラメーター（OSS利用時）：**

| パラメーター名 | 設定ファイル | 設定値 | 備考 |
|-------------|-----------|--------|------|
| `DatabaseDirectory` | `/etc/clamd.d/scan.conf` | /var/lib/clamav | ウイルス定義DB |
| `LocalSocket` | `/etc/clamd.d/scan.conf` | /run/clamd.scan/clamd.sock | |
| `LogFile` | `/etc/clamd.d/scan.conf` | /var/log/clamd.scan | |
| `ScanOnAccess` | `/etc/clamd.d/scan.conf` | yes | アクセス時スキャン（オンアクセス） |
| 定義更新スケジュール | systemd timer | 日次 03:00 | `freshclam` コマンド |

---

## 🔷 26. 監視設定パラメーター

**監視ツール：Zabbix Agent 2（推奨）または Prometheus node_exporter**

**Zabbix Agent 2 設定（`/etc/zabbix/zabbix_agent2.conf`）：**

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `Server` | ★ZabbixサーバーIP | 監視サーバーのIP |
| `ServerActive` | ★ZabbixサーバーIP | アクティブチェック用 |
| `Hostname` | ★監視対象ホスト名 | Zabbix管理画面の名称 |
| `LogFile` | /var/log/zabbix/zabbix_agent2.log | エージェントログ |
| `LogFileSize` | 10 | ログファイルサイズ（MB） |
| `Timeout` | 10 | タイムアウト（秒） |
| `AllowKey=system.run[*]` | （記載） | リモートコマンド許可（必要な場合のみ） |
| `UserParameter` | ★カスタム監視項目 | 独自監視スクリプト |

**監視項目・閾値設定：**

| 監視項目 | キー（Zabbix） | 警告閾値 | 重大閾値 | 監視間隔 |
|---------|------------|---------|---------|---------|
| CPU使用率 | system.cpu.util | 80% | 95% | 60秒 |
| Memory使用率 | vm.memory.utilization | 80% | 95% | 60秒 |
| Disk使用率 | vfs.fs.size[/,pused] | 80% | 90% | 300秒 |
| inode使用率 | vfs.fs.inode[/,pused] | 80% | 90% | 300秒 |
| Load Average（1分） | system.cpu.load[percpu,avg1] | CPU×2 | CPU×4 | 60秒 |
| プロセス監視（httpd） | proc.num[httpd] | 0（停止） | — | 60秒 |
| TCPポート（443） | net.tcp.port[,443] | 応答なし | — | 60秒 |
| SSL証明書期限 | web.certificate.get | 30日前 | 7日前 | 1日 |
| NTP同期状態 | timedatectl同期確認 | 未同期 | — | 300秒 |

**Prometheus node_exporter設定：**

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| Listen Port | :9100 | node_exporterデフォルトポート |
| TLS設定 | 推奨（`--web.config.file`） | Prometheus → exporter間TLS |
| 収集項目 | cpu / memory / disk / netstat / filesystem | デフォルト有効 |
| firewalld許可 | TCP 9100 / internal zone | Prometheusサーバーからのみ許可 |

---

## 🔷 27. パッチ管理設定パラメーター

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| 定例パッチ実行コマンド | `dnf update --security -y` | セキュリティパッチのみ |
| 全体更新コマンド | `dnf update -y` | 全パッケージ更新 |
| パッチ確認コマンド | `dnf check-update --security` | 適用前の確認 |
| 脆弱性情報確認 | `dnf updateinfo list security` | CVE情報一覧 |
| 定例パッチ実行スケジュール | 月次（毎月第2水曜 02:00） | ★プロジェクトで確定 |
| 緊急パッチ判断基準 | CVSS Score 7.0以上 | 即日対応 |
| 適用前スナップショット | 必須（VM環境） | ロールバック手段確保 |
| カーネル更新後作業 | `reboot` + サービス起動確認 | メンテナンスウィンドウ内 |

**systemd timerによる月次パッチ適用（`/etc/systemd/system/monthly-patch.timer`）：**

```ini
[Unit]
Description=Monthly security patch

[Timer]
# 毎月第2水曜日 02:00
OnCalendar=Wed *-*-8..14 02:00:00
RandomizedDelaySec=1800
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
[Unit]
Description=Apply security patches

[Service]
Type=oneshot
ExecStart=/usr/bin/dnf update -y --security
ExecStartPost=/usr/bin/systemctl reboot
```

> **注意**：自動rebootは非推奨。カーネル更新時のみ手動でメンテナンスウィンドウ内に再起動すること。

---

## 🔷 28. sudo設定パラメーター

**管理方針**：`/etc/sudoers.d/` 配下にロール別ファイルを作成。`visudo` で編集必須。

| ロール | ファイルパス | 付与コマンド | NOPASSWD |
|-------|------------|------------|---------|
| 運用管理者 | `/etc/sudoers.d/ops` | systemctl / journalctl / nmcli / ss | 任意 |
| DB管理者 | `/etc/sudoers.d/dba` | mysqldump / pg_dump / DBサービス操作 | 任意 |
| AP管理者 | `/etc/sudoers.d/app` | httpd/nginx 起動停止 / デプロイスクリプト | 任意 |
| セキュリティ担当 | `/etc/sudoers.d/sec` | aide / fail2ban-client / auditctl / aureport | 任意 |

**設定ファイル例：**

```
# /etc/sudoers.d/ops
# 運用管理者グループ（ops）の権限
%ops ALL=(ALL) NOPASSWD: /bin/systemctl, \
                          /usr/bin/journalctl, \
                          /usr/sbin/nmcli, \
                          /usr/sbin/ss

# /etc/sudoers.d/dba
# DB管理者グループ（dba）の権限
%dba ALL=(ALL) NOPASSWD: /usr/bin/mysqldump, \
                          /usr/bin/pg_dump, \
                          /bin/systemctl restart mysqld, \
                          /bin/systemctl restart postgresql

# /etc/sudoers.d/app
# AP管理者グループ（app）の権限
%app ALL=(ALL) NOPASSWD: /bin/systemctl restart httpd, \
                          /bin/systemctl restart nginx, \
                          /usr/local/bin/deploy.sh

# /etc/sudoers.d/sec
# セキュリティ担当グループ（sec）の権限
%sec ALL=(ALL) NOPASSWD: /usr/sbin/aide, \
                          /usr/bin/fail2ban-client, \
                          /usr/sbin/auditctl, \
                          /usr/sbin/aureport
```

確認コマンド：
```bash
visudo -c              # sudoers構文チェック
sudo -l -U ★ユーザー名  # ユーザーのsudo権限確認
```

---

## 🔷 29. サービス自動復旧設定パラメーター

**管理方法**：Drop-inファイル `/etc/systemd/system/★.service.d/restart.conf` で設定

| サービス | Drop-inファイルパス | Restart | RestartSec | StartLimitBurst |
|---------|------------------|---------|-----------|----------------|
| httpd | /etc/systemd/system/httpd.service.d/restart.conf | always | 10秒 | 5（60秒内） |
| nginx | /etc/systemd/system/nginx.service.d/restart.conf | always | 10秒 | 5（60秒内） |
| postfix | /etc/systemd/system/postfix.service.d/restart.conf | always | 10秒 | 5（60秒内） |
| named | /etc/systemd/system/named.service.d/restart.conf | always | 10秒 | 5（60秒内） |
| sshd | /etc/systemd/system/sshd.service.d/restart.conf | always | 5秒 | 5（60秒内） |
| chronyd | /etc/systemd/system/chronyd.service.d/restart.conf | always | 30秒 | 5（60秒内） |

**Drop-inファイルテンプレート：**

```ini
# /etc/systemd/system/httpd.service.d/restart.conf
[Unit]
StartLimitBurst=5
StartLimitIntervalSec=60

[Service]
Restart=always
RestartSec=10
```

適用コマンド：
```bash
systemctl daemon-reload
systemctl restart ★サービス名
systemctl show ★サービス名 | grep -E "Restart|StartLimit"
```

---

## 🔷 30. 運用管理サービス設定パラメーター

### ▶️ 30.1 SSH公開鍵集中管理（FreeIPA連携）

**設定ファイル**：`/etc/ssh/sshd_config`（追記）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `AuthorizedKeysCommand` | /usr/bin/sss_ssh_authorizedkeys %u | SSSD経由でFreeIPAから公開鍵取得 |
| `AuthorizedKeysCommandUser` | nobody | 実行ユーザー（最小権限） |

```
# /etc/ssh/sshd_config に追記
AuthorizedKeysCommand /usr/bin/sss_ssh_authorizedkeys %u
AuthorizedKeysCommandUser nobody
```

### ▶️ 30.2 Ansible構成管理パラメーター

**設定ファイル**：`/etc/ansible/ansible.cfg` または `ansible.cfg`（プロジェクトルート）

| パラメーター名 | 設定値 | 備考 |
|-------------|--------|------|
| `inventory` | ./inventory/ | インベントリディレクトリ |
| `remote_user` | ★管理ユーザー名 | SSH接続ユーザー |
| `private_key_file` | ~/.ssh/★管理鍵 | Ed25519鍵推奨 |
| `host_key_checking` | True | ホスト鍵確認（本番環境は必須） |
| `stdout_callback` | yaml | 出力フォーマット |
| `log_path` | /var/log/ansible.log | Ansibleログ |
| `roles_path` | ./roles | ロールパス |
| `forks` | 10 | 並列実行数 |
| `timeout` | 30 | SSH接続タイムアウト（秒） |
| `become` | True | デフォルトsudo昇格 |
| `become_method` | sudo | 昇格方式 |

**実行コマンド例：**

```bash
# 構文チェック
ansible-playbook site.yml --syntax-check

# ドライラン（変更なし確認）
ansible-playbook site.yml --check --diff

# 本番適用
ansible-playbook site.yml -i inventory/production

# パッチ適用Playbook
ansible-playbook patch.yml -i inventory/production --limit web-servers

# 特定タグのみ実行
ansible-playbook site.yml --tags "security,monitoring"
```
