# SRE向け Windows PowerShell コマンド集【Windows Server用】

> よく使うコマンドのクイックリファレンス  
> 対象：Windows Server の運用・監視・インフラ管理（SRE業務）

---

## 目次

1. [サーバー情報・リソース監視](#1-サーバー情報リソース監視)
2. [リモート操作](#2-リモート操作)
3. [パフォーマンスカウンター](#3-パフォーマンスカウンター)
4. [IIS管理](#4-iis管理)
5. [Active Directory管理](#5-active-directory管理)
6. [Windows Server Update管理](#6-windows-server-update管理)
7. [AWS Systems Manager（SSM）](#7-aws-systems-managerssm)

---

## 1. サーバー情報・リソース監視

```powershell
# OS・ホスト情報
Get-ComputerInfo | Select-Object CsName, OsName, OsVersion, WindowsInstallationType

# CPU使用率
Get-WmiObject Win32_Processor | Select-Object Name, LoadPercentage, NumberOfCores

# メモリ使用状況（GB換算）
Get-WmiObject Win32_OperatingSystem | Select-Object `
  @{N="TotalGB"; E={[math]::Round($_.TotalVisibleMemorySize/1MB,2)}}, `
  @{N="FreeGB";  E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}, `
  @{N="UsedGB";  E={[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)/1MB,2)}}

# サーバー稼働時間
(Get-Date) - (gcim Win32_OperatingSystem).LastBootUpTime

# ディスク空き容量（全ドライブ）
Get-WmiObject Win32_LogicalDisk | `
  Select-Object DeviceID, `
    @{N="SizeGB"; E={[math]::Round($_.Size/1GB,2)}}, `
    @{N="FreeGB"; E={[math]::Round($_.FreeSpace/1GB,2)}}, `
    @{N="Free%";  E={[math]::Round($_.FreeSpace/$_.Size*100,1)}}

# CPU・メモリをリアルタイム監視（5秒間隔 × 12回 = 1分）
1..12 | ForEach-Object {
  $cpu    = (Get-WmiObject Win32_Processor | Measure-Object LoadPercentage -Average).Average
  $mem    = Get-WmiObject Win32_OperatingSystem
  $freeGB = [math]::Round($mem.FreePhysicalMemory/1MB, 2)
  Write-Host "$(Get-Date -Format 'HH:mm:ss') | CPU: ${cpu}% | MemFree: ${freeGB}GB"
  Start-Sleep -Seconds 5
}

# サーバーサマリー（SRE用・自動停止サービス検知付き）
function Show-ServerSummary {
  $os     = Get-WmiObject Win32_OperatingSystem
  $cpu    = (Get-WmiObject Win32_Processor | Measure-Object LoadPercentage -Average).Average
  $uptime = (Get-Date) - $os.ConvertToDateTime($os.LastBootUpTime)
  Write-Host "=== Server SRE Summary ===" -ForegroundColor Green
  Write-Host "Host    : $env:COMPUTERNAME"
  Write-Host "OS      : $($os.Caption)"
  Write-Host "Uptime  : $([math]::Round($uptime.TotalDays,1)) days"
  Write-Host "CPU     : ${cpu}%"
  Write-Host "MemFree : $([math]::Round($os.FreePhysicalMemory/1MB,2)) GB / $([math]::Round($os.TotalVisibleMemorySize/1MB,2)) GB"
  Write-Host "--- Disk ---"
  Get-WmiObject Win32_LogicalDisk | ForEach-Object {
    Write-Host "  $($_.DeviceID) Free: $([math]::Round($_.FreeSpace/1GB,1))GB / $([math]::Round($_.Size/1GB,1))GB"
  }
  Write-Host "--- Stopped Auto Services ---"
  Get-Service | Where-Object { $_.Status -eq "Stopped" -and $_.StartType -eq "Automatic" } | `
    Select-Object Name, DisplayName | Format-Table -AutoSize
}
Show-ServerSummary
```

---

## 2. リモート操作

```powershell
# WinRM有効化（サーバー側で実行）
Enable-PSRemoting -Force

# WinRM疎通確認
Test-WSMan -ComputerName "server01"

# リモートセッション開始
Enter-PSSession -ComputerName "server01" -Credential (Get-Credential)

# リモートコマンド実行（単発）
Invoke-Command -ComputerName "server01" -ScriptBlock { Get-Service }

# 複数サーバーへ一括実行
$servers = @("server01", "server02", "server03")
Invoke-Command -ComputerName $servers -ScriptBlock {
  [PSCustomObject]@{
    Host   = $env:COMPUTERNAME
    CPU    = (Get-WmiObject Win32_Processor | Measure-Object LoadPercentage -Average).Average
    FreeGB = [math]::Round((Get-WmiObject Win32_OperatingSystem).FreePhysicalMemory/1MB, 2)
  }
}

# リモートへのファイルコピー（UNCパス経由）
Copy-Item -Path "C:\config.json" -Destination "\\server01\C$\app\" -Force

# リモートセッション経由でファイルコピー（PSSession使用）
$session = New-PSSession -ComputerName "server01"
Copy-Item -Path "C:\deploy\app.zip" -Destination "C:\deploy\" -ToSession $session
Remove-PSSession $session
```

---

## 3. パフォーマンスカウンター

```powershell
# CPU使用率
Get-Counter "\Processor(_Total)\% Processor Time"

# 利用可能メモリ（MB）
Get-Counter "\Memory\Available MBytes"

# ディスクI/O
Get-Counter "\PhysicalDisk(_Total)\% Disk Time"
Get-Counter "\PhysicalDisk(_Total)\Avg. Disk Queue Length"

# ネットワーク使用量
Get-Counter "\Network Interface(*)\Bytes Total/sec"

# 複数カウンターを同時取得（5秒間隔 × 6回）
Get-Counter @(
  "\Processor(_Total)\% Processor Time",
  "\Memory\Available MBytes",
  "\PhysicalDisk(_Total)\Avg. Disk Queue Length"
) -SampleInterval 5 -MaxSamples 6

# IIS固有カウンター（IIS稼働サーバーのみ）
Get-Counter "\Web Service(_Total)\Current Connections"
Get-Counter "\Web Service(_Total)\Total Method Requests/sec"

# カウンターをCSVに記録（10分間）
Get-Counter @(
  "\Processor(_Total)\% Processor Time",
  "\Memory\Available MBytes"
) -SampleInterval 10 -MaxSamples 60 |
  Export-Counter -Path "C:\Logs\perf_$(Get-Date -Format 'yyyyMMdd_HHmm').csv" -FileFormat CSV
```

---

## 4. IIS管理

```powershell
# WebAdministrationモジュール読み込み（IIS操作の前提）
Import-Module WebAdministration

# Webサイト一覧
Get-WebSite

# アプリケーションプール一覧
Get-WebConfiguration system.applicationHost/applicationPools/add | `
  Select-Object name, state, managedRuntimeVersion

# サイトの起動・停止
Start-WebSite -Name "Default Web Site"
Stop-WebSite  -Name "Default Web Site"

# アプリプールの起動・停止・リサイクル
Start-WebAppPool   -Name "DefaultAppPool"
Stop-WebAppPool    -Name "DefaultAppPool"
Restart-WebAppPool -Name "DefaultAppPool"

# 停止中のアプリプール一覧
Get-WebConfiguration system.applicationHost/applicationPools/add | `
  Where-Object { $_.state -eq "Stopped" } | Select-Object name, state

# IISサービス状態確認・再起動
Get-Service -Name "W3SVC"
Restart-Service -Name "W3SVC" -Force

# バインディング（ポート・ホスト名）確認
Get-WebBinding | Select-Object bindingInformation, protocol, itemXPath

# 特定サイトのバインディング確認
Get-WebBinding -Name "Default Web Site"

# アクセスログのパス確認
Get-WebConfigurationProperty `
  -Filter "system.applicationHost/sites/site[@name='Default Web Site']/logFile" `
  -Name directory

# IISログのエラー（HTTP 500系）をgrep
Select-String -Path "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Pattern " 5[0-9][0-9] " | `
  Select-Object -Last 50

# IISリセット
iisreset
iisreset /status   # 状態確認のみ
```

---

## 5. Active Directory管理

```powershell
# モジュール読み込み（RSAT-AD-PowerShellが必要）
Import-Module ActiveDirectory

# ドメイン情報確認
Get-ADDomain | Select-Object Name, DNSRoot, DomainControllers

# ドメインコントローラー一覧
Get-ADDomainController -Filter * | Select-Object Name, IPv4Address, Site, OperatingSystem

# ユーザー検索
Get-ADUser -Filter { Name -like "*yamada*" } | Select-Object Name, SamAccountName, Enabled

# ユーザーの詳細情報
Get-ADUser -Identity "yamada.taro" -Properties * | `
  Select-Object Name, SamAccountName, EmailAddress, LastLogonDate, PasswordLastSet, Enabled

# 無効化されたユーザー一覧
Get-ADUser -Filter { Enabled -eq $false } | Select-Object Name, SamAccountName

# パスワード期限切れユーザー一覧
Search-ADAccount -PasswordExpired | Select-Object Name, SamAccountName, PasswordExpired

# ロックアウトされたユーザー確認・解除
Search-ADAccount -LockedOut | Select-Object Name, SamAccountName
Unlock-ADAccount -Identity "yamada.taro"

# グループのメンバー確認
Get-ADGroupMember -Identity "Domain Admins" | Select-Object Name, SamAccountName, objectClass

# ユーザーが所属するグループ一覧
Get-ADPrincipalGroupMembership -Identity "yamada.taro" | Select-Object Name, GroupCategory

# コンピューターアカウント一覧（最終ログオン日時付き）
Get-ADComputer -Filter * -Properties LastLogonDate | `
  Select-Object Name, LastLogonDate, OperatingSystem | Sort-Object LastLogonDate -Descending

# DCとのレプリケーション状態確認
repadmin /showrepl
repadmin /replsummary
```

---

## 6. Windows Server Update管理

```powershell
# PSWindowsUpdateモジュールのインストール（初回のみ）
Install-Module -Name PSWindowsUpdate -Force -Scope AllUsers
Import-Module PSWindowsUpdate

# 利用可能な更新プログラム一覧
Get-WindowsUpdate

# セキュリティ更新のみ確認
Get-WindowsUpdate -Category "Security Updates"

# 更新プログラムのダウンロードのみ（インストールしない）
Get-WindowsUpdate -Download

# 更新プログラムのインストール（自動承認・再起動あり）
Install-WindowsUpdate -AcceptAll -AutoReboot

# 再起動なしでインストール（メンテナンス窓外でのテスト向け）
Install-WindowsUpdate -AcceptAll -IgnoreReboot

# 特定KBのみインストール
Get-WindowsUpdate -KBArticleID "KB5031455" | Install-WindowsUpdate -AcceptAll

# インストール済み更新履歴
Get-WUHistory | Select-Object -First 20 Title, Date, Result

# 保留中の再起動確認
Get-WURebootStatus

# Windows Updateサービス状態確認
Get-Service -Name wuauserv | Select-Object Name, Status, StartType

# 更新プログラムのアンインストール（ロールバック）
wusa /uninstall /kb:5031455 /quiet /norestart

# インストール済みHotFix一覧
Get-HotFix | Sort-Object InstalledOn -Descending | `
  Select-Object -First 20 HotFixID, InstalledOn, Description

# 複数サーバーへのWindows Update状況一括確認
$servers = @("server01", "server02", "server03")
Invoke-Command -ComputerName $servers -ScriptBlock {
  Import-Module PSWindowsUpdate
  $updates = Get-WindowsUpdate
  [PSCustomObject]@{
    Host         = $env:COMPUTERNAME
    PendingCount = $updates.Count
  }
}
```

---

## 7. AWS Systems Manager（SSM）

```powershell
# AWS Tools for PowerShellのインストール（初回のみ）
Install-Module -Name AWS.Tools.SimpleSystemsManagement -Force
Import-Module AWS.Tools.SimpleSystemsManagement

# 認証・リージョン設定
Set-AWSCredential -ProfileName "default"
Set-DefaultAWSRegion -Region "ap-northeast-1"

# SSM管理対象インスタンス一覧
Get-SSMInstanceInformation | `
  Select-Object InstanceId, ComputerName, PingStatus, PlatformName, AgentVersion

# オンライン（接続中）のインスタンスのみ表示
Get-SSMInstanceInformation | Where-Object { $_.PingStatus -eq "Online" } | `
  Select-Object InstanceId, ComputerName, PlatformName

# --- Run Command（リモートコマンド実行）---

# 単一インスタンスにPowerShellコマンドを実行
$cmd = Send-SSMCommand `
  -InstanceId "i-0123456789abcdef0" `
  -DocumentName "AWS-RunPowerShellScript" `
  -Parameter @{ commands = @("Get-Service | Where-Object { `$_.Status -eq 'Stopped' }") }

# コマンド実行結果の確認
Get-SSMCommandInvocation -CommandId $cmd.CommandId -Details $true | `
  Select-Object -ExpandProperty CommandPlugins | Select-Object Output, ResponseCode

# 複数インスタンスへ一括実行（タグでフィルタ）
$cmd = Send-SSMCommand `
  -Target @(@{ Key = "tag:Environment"; Values = @("Production") }) `
  -DocumentName "AWS-RunPowerShellScript" `
  -Parameter @{ commands = @("Show-ServerSummary") }

# 実行状況の確認
Get-SSMCommand -CommandId $cmd.CommandId | `
  Select-Object Status, TargetCount, CompletedCount, ErrorCount

# --- Session Manager（対話型セッション）---
# ※AWS CLIが必要（WinRM不要・ポート開放不要）
aws ssm start-session --target i-0123456789abcdef0

# --- Parameter Store ---

# パラメータ一覧
Get-SSMParameterList | Select-Object Name, Type, LastModifiedDate

# パラメータ値の取得（SecureString含む）
(Get-SSMParameter -Name "/myapp/db/password" -WithDecryption $true).Parameter.Value

# パラメータの作成・更新
Write-SSMParameter -Name "/myapp/db/host" -Value "db.example.com" -Type String -Overwrite $true

# パラメータの削除
Remove-SSMParameter -Name "/myapp/db/old-key" -Force

# --- Patch Manager ---

# パッチコンプライアンス状態確認
Get-SSMPatchSummary -InstanceId "i-0123456789abcdef0"

# パッチが未適用のインスタンスを一覧
Get-SSMInstancePatchStatesForPatchGroup -PatchGroup "Production" | `
  Where-Object { $_.MissingCount -gt 0 } | Select-Object InstanceId, MissingCount, FailedCount
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
> - `Stop-Process`、`Stop-Service` は本番環境では十分確認してから実行すること
> - WMI系コマンドは `Get-CimInstance`（PowerShell 3.0以降推奨）でも代替可能
> - リモート操作には WinRM の有効化が必要（`Enable-PSRemoting -Force`）
> - SSMのRun Commandは IAMロール（AmazonSSMManagedInstanceCore）とSSMエージェントが必要
> - AD管理コマンドは RSAT（リモートサーバー管理ツール）のインストールが前提
> - PSWindowsUpdate はデフォルトでは未インストール。事前に `Install-Module` が必要
