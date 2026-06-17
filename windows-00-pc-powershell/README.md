# SRE向け Windows PowerShell コマンド集【Windows PC用】

> よく使うコマンドのクイックリファレンス  
> 対象：開発PC・管理端末での日常操作・調査・メンテナンス

---

## 目次

1. [システム情報・リソース確認](#1-システム情報リソース確認)
2. [プロセス管理](#2-プロセス管理)
3. [サービス管理](#3-サービス管理)
4. [ネットワーク確認・診断](#4-ネットワーク確認診断)
5. [ディスク・ファイルシステム](#5-ディスクファイルシステム)
6. [イベントログ・ログ解析](#6-イベントログログ解析)
7. [ユーザー・権限管理](#7-ユーザー権限管理)
8. [スケジュールタスク](#8-スケジュールタスク)
9. [Windows Update管理](#9-windows-update管理)
10. [便利なワンライナー](#10-便利なワンライナー)

---

## 1. システム情報・リソース確認

```powershell
# OS・ホスト情報
Get-ComputerInfo | Select-Object CsName, OsName, OsVersion, OsArchitecture

# OS情報（簡易）
[System.Environment]::OSVersion

# CPU使用率（現時点）
Get-WmiObject Win32_Processor | Select-Object Name, LoadPercentage

# メモリ使用状況（GB換算）
Get-WmiObject Win32_OperatingSystem | Select-Object `
  @{N="TotalGB"; E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, `
  @{N="FreeGB";  E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}, `
  @{N="UsedGB";  E={[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)/1MB,2)}}

# システム稼働時間
(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime

# ホスト名確認
$env:COMPUTERNAME
[System.Net.Dns]::GetHostName()

# インストール済みソフトウェア一覧
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
  Select-Object DisplayName, DisplayVersion, Publisher | Sort-Object DisplayName

# 電源プラン確認
powercfg /list

# BitLocker状態確認
manage-bde -status C:
```

---

## 2. プロセス管理

```powershell
# 実行中プロセス一覧（CPU使用率降順）
Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 Name, Id, CPU, WorkingSet

# プロセス名で検索
Get-Process -Name "chrome"

# プロセスIDで詳細確認
Get-Process -Id 1234 | Format-List *

# プロセスの強制終了
Stop-Process -Name "notepad" -Force
Stop-Process -Id 1234 -Force

# メモリ500MB超のプロセス一覧
Get-Process | Where-Object { $_.WorkingSet -gt 500MB } | `
  Select-Object Name, Id, @{N="MemMB"; E={[math]::Round($_.WorkingSet/1MB,1)}} | `
  Sort-Object MemMB -Descending

# 特定プロセスのCPU・メモリ監視（10秒間隔）
while ($true) {
  Get-Process -Name "chrome" | `
    Select-Object Name, CPU, @{N="MemMB"; E={[math]::Round($_.WorkingSet/1MB,1)}}
  Start-Sleep -Seconds 10
}
```

---

## 3. サービス管理

```powershell
# 全サービス一覧
Get-Service

# サービスの状態確認
Get-Service -Name "wuauserv"

# 停止中のサービス一覧
Get-Service | Where-Object { $_.Status -eq "Stopped" }

# サービスの起動・停止・再起動
Start-Service   -Name "Spooler"
Stop-Service    -Name "Spooler"
Restart-Service -Name "Spooler" -Force

# スタートアップ種別変更（自動/手動/無効）
Set-Service -Name "wuauserv" -StartupType Automatic
Set-Service -Name "wuauserv" -StartupType Disabled

# サービスの詳細情報（実行ユーザー含む）
Get-WmiObject Win32_Service | Where-Object { $_.Name -eq "Spooler" } | `
  Select-Object Name, State, StartMode, StartName, PathName
```

---

## 4. ネットワーク確認・診断

```powershell
# IPアドレス・NIC情報
Get-NetIPAddress | Where-Object { $_.AddressFamily -eq "IPv4" }

# ルーティングテーブル
Get-NetRoute

# DNSサーバー確認
Get-DnsClientServerAddress

# 接続中のTCP接続一覧（ESTABLISHED）
Get-NetTCPConnection | Where-Object { $_.State -eq "Established" } | `
  Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State

# ポートリスン確認
Get-NetTCPConnection | Where-Object { $_.State -eq "Listen" } | `
  Select-Object LocalAddress, LocalPort | Sort-Object LocalPort

# ping
Test-Connection -ComputerName "google.com" -Count 4

# Traceroute
Test-NetConnection -ComputerName "google.com" -TraceRoute

# ポート疎通確認
Test-NetConnection -ComputerName "10.0.0.1" -Port 443

# DNS名前解決
Resolve-DnsName "example.com"

# プロキシ設定確認
netsh winhttp show proxy

# Wi-Fi接続プロファイル一覧
netsh wlan show profiles

# ファイアウォールルール確認
Get-NetFirewallRule | Where-Object { $_.Enabled -eq "True" } | `
  Select-Object Name, Direction, Action, DisplayName
```

---

## 5. ディスク・ファイルシステム

```powershell
# ディスク使用量（全ドライブ）
Get-PSDrive -PSProvider FileSystem | `
  Select-Object Name, @{N="UsedGB"; E={[math]::Round(($_.Used/1GB),2)}}, `
                       @{N="FreeGB"; E={[math]::Round(($_.Free/1GB),2)}}

# ディスク情報詳細（WMI）
Get-WmiObject Win32_LogicalDisk | `
  Select-Object DeviceID, `
    @{N="SizeGB"; E={[math]::Round($_.Size/1GB,2)}}, `
    @{N="FreeGB"; E={[math]::Round($_.FreeSpace/1GB,2)}}, `
    @{N="Free%";  E={[math]::Round($_.FreeSpace/$_.Size*100,1)}}

# 大きいファイルを探す（上位10件）
Get-ChildItem -Path "C:\" -Recurse -ErrorAction SilentlyContinue | `
  Sort-Object Length -Descending | Select-Object -First 10 FullName, `
  @{N="SizeMB"; E={[math]::Round($_.Length/1MB,2)}}

# フォルダサイズ計算
(Get-ChildItem -Path "C:\Users" -Recurse -ErrorAction SilentlyContinue | `
  Measure-Object -Property Length -Sum).Sum / 1GB

# ファイル検索
Get-ChildItem -Path "C:\Users" -Filter "*.log" -Recurse -ErrorAction SilentlyContinue

# 古いファイルの検索（30日以上更新なし）
Get-ChildItem -Path "C:\Temp" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }

# 一時ファイルの削除
Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## 6. イベントログ・ログ解析

```powershell
# システムログの最新50件
Get-EventLog -LogName System -Newest 50

# エラー・警告のみ抽出
Get-EventLog -LogName System -EntryType Error, Warning -Newest 100

# アプリケーションログのエラー（直近1時間）
$since = (Get-Date).AddHours(-1)
Get-EventLog -LogName Application -EntryType Error -After $since

# 特定イベントID（例：4625 ログオン失敗）
Get-EventLog -LogName Security -InstanceId 4625 -Newest 50

# WinEventで詳細フィルタ
Get-WinEvent -LogName "System" -MaxEvents 50 | `
  Where-Object { $_.LevelDisplayName -eq "Error" }

# ログをCSVエクスポート
Get-EventLog -LogName System -EntryType Error -Newest 100 | `
  Export-Csv -Path "$env:USERPROFILE\Desktop\system_errors.csv" -Encoding UTF8 -NoTypeInformation

# クラッシュダンプの確認
Get-EventLog -LogName System -Source "Microsoft-Windows-WER-SystemErrorReporting" -Newest 10
```

---

## 7. ユーザー・権限管理

```powershell
# ローカルユーザー一覧
Get-LocalUser

# ローカルグループ一覧
Get-LocalGroup

# Administratorsグループのメンバー確認
Get-LocalGroupMember -Group "Administrators"

# 現在ログイン中のユーザー
query user

# 現在の実行ユーザー確認
whoami
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# 管理者権限チェック
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).`
  IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# 管理者として再起動（UAC昇格）
Start-Process powershell -Verb RunAs

# ユーザーのSID確認
(New-Object System.Security.Principal.NTAccount("username")).`
  Translate([System.Security.Principal.SecurityIdentifier]).Value
```

---

## 8. スケジュールタスク

```powershell
# タスク一覧
Get-ScheduledTask

# 実行中のタスクのみ
Get-ScheduledTask | Where-Object { $_.State -eq "Running" }

# タスクの状態確認
Get-ScheduledTask -TaskName "MyBackupTask" | Select-Object TaskName, State

# タスクの手動実行
Start-ScheduledTask -TaskName "MyBackupTask"

# タスクの有効化・無効化
Enable-ScheduledTask  -TaskName "MyBackupTask"
Disable-ScheduledTask -TaskName "MyBackupTask"

# タスクの詳細情報（実行履歴含む）
Get-ScheduledTaskInfo -TaskName "MyBackupTask"

# 新規タスク登録（例：毎日22時にスクリプト実行）
$action  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\Scripts\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "22:00"
Register-ScheduledTask -TaskName "DailyBackup" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## 9. Windows Update管理

```powershell
# PSWindowsUpdateモジュールのインストール（初回のみ）
Install-Module -Name PSWindowsUpdate -Force -Scope CurrentUser
Import-Module PSWindowsUpdate

# 利用可能な更新プログラム確認
Get-WindowsUpdate

# セキュリティ更新のみ確認
Get-WindowsUpdate -Category "Security Updates"

# 更新プログラムのインストール（自動承認）
Install-WindowsUpdate -AcceptAll -AutoReboot

# 再起動なしでインストール
Install-WindowsUpdate -AcceptAll -IgnoreReboot

# インストール済み更新履歴
Get-WUHistory | Select-Object -First 20 Title, Date, Result

# 保留中の再起動確認
Get-WURebootStatus

# インストール済みHotFix一覧
Get-HotFix | Sort-Object InstalledOn -Descending | `
  Select-Object -First 20 HotFixID, InstalledOn, Description
```

---

## 10. 便利なワンライナー

```powershell
# PCの状態を素早くサマリー表示
function Show-PCSummary {
  $os     = Get-WmiObject Win32_OperatingSystem
  $cpu    = (Get-WmiObject Win32_Processor | Measure-Object LoadPercentage -Average).Average
  $uptime = (Get-Date) - $os.ConvertToDateTime($os.LastBootUpTime)
  Write-Host "=== PC Summary ===" -ForegroundColor Cyan
  Write-Host "Host    : $env:COMPUTERNAME"
  Write-Host "User    : $env:USERNAME"
  Write-Host "Uptime  : $([math]::Round($uptime.TotalHours,1)) hours"
  Write-Host "CPU     : ${cpu}%"
  Write-Host "MemFree : $([math]::Round($os.FreePhysicalMemory/1MB,2)) GB"
  Get-PSDrive -PSProvider FileSystem | ForEach-Object {
    Write-Host "Disk $($_.Name): Free $([math]::Round($_.Free/1GB,1))GB"
  }
}
Show-PCSummary

# ログファイルをリアルタイムでtail（Linux の tail -f 相当）
Get-Content -Path "C:\Logs\app.log" -Wait -Tail 30

# 特定文字列を含む行だけ抽出（grep相当）
Select-String -Path "C:\Logs\app.log" -Pattern "ERROR|WARN" | Select-Object -Last 50

# クリップボードにコマンド結果をコピー
Get-Process | Out-String | Set-Clipboard

# 直近のエラーイベントを素早く確認
Get-WinEvent -LogName System -MaxEvents 200 | Where-Object LevelDisplayName -eq "Error" | `
  Select-Object TimeCreated, Id, Message | Format-Table -AutoSize

# ポート一覧をプロセス名付きで表示
Get-NetTCPConnection -State Listen | ForEach-Object {
  $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
  [PSCustomObject]@{ Port = $_.LocalPort; PID = $_.OwningProcess; Process = $proc.Name }
} | Sort-Object Port

# 環境変数一覧
Get-ChildItem Env: | Sort-Object Name
```

---

## Tips

| 操作 | コマンド |
|------|---------|
| コマンド履歴 | `Get-History` / `h` |
| エイリアス確認 | `Get-Alias` |
| モジュール一覧 | `Get-Module -ListAvailable` |
| ヘルプ表示 | `Get-Help <コマンド> -Examples` |
| オブジェクト構造確認 | `Get-Process \| Get-Member` |
| 変数一覧 | `Get-Variable` |
| エラー詳細 | `$Error[0] \| Format-List *` |
| 実行ポリシー確認 | `Get-ExecutionPolicy` |
| 実行ポリシー変更 | `Set-ExecutionPolicy RemoteSigned` |
| 管理者で起動 | `Start-Process powershell -Verb RunAs` |

---

> **注意事項**
> - `Stop-Process`、`Stop-Service` は十分確認してから実行すること
> - WMI系コマンドは `Get-CimInstance`（PowerShell 3.0以降推奨）でも代替可能
> - PSWindowsUpdate はデフォルトでは未インストール。事前に `Install-Module` が必要
