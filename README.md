# QuickPic Gallery Mod — SMBv2/v3 升级与深度修复版 (64-bit Pure Java)

[![Platform](https://img.shields.io/badge/Platform-Android%208.0%2B%20(API%2026--35)-3DDC84?logo=android)](https://www.android.com/)
[![ABI](https://img.shields.io/badge/ABI-64--bit%20Pure%20Java%20(All%20Arch)-blue)](#4-纯-java-64-位图像引擎与-gifwebp-动图支持)
[![SMB](https://img.shields.io/badge/SMB-v1%20%7C%20v2.02%20%7C%20v2.1%20%7C%20v3.0%20%7C%20v3.1.1-orange)](#1-原生支持-smbv1--smbv2--smbv3最高-smb-311)

本项目是对经典安卓图库 **快图浏览（QuickPic Gallery）** 社区修改版的深度修复与协议升级版本。在整合各大社区分支优秀特性的基础上，彻底解决了长期困扰用户的 **仅支持老旧 SMBv1 协议**、**SMB 浏览切后台回主页丢失状态**、**高版本 Android 搜索崩溃 (`SecurityException`)**、**64 位 `.so` 魔改导致的界面异常** 以及 **友盟统计/自更新残留引发的杀毒软件误报 (`a.gray.devicemaster.a`)** 等核心问题。

---

## 目录

- [核心修复与升级一览](#核心修复与升级一览)
- [安装包版本对比与下载](#安装包版本对比与下载)
- [技术原理与根因分析](#技术原理与根因分析)
  - [1. 原生支持 SMBv1 / SMBv2 / SMBv3（最高 SMB 3.1.1）](#1-原生支持-smbv1--smbv2--smbv3最高-smb-311)
  - [2. 修复 SMB/云端目录切后台或锁屏后回到主页的问题](#2-修复-smb云端目录切后台或锁屏后回到主页的问题)
  - [3. 修复搜索功能崩溃 (`SecurityException: Failed to find provider`)](#3-修复搜索功能崩溃-securityexception-failed-to-find-provider)
  - [4. 纯 Java 64 位图像引擎与 GIF/WebP 动图支持](#4-纯-java-64-位图像引擎与-gifwebp-动图支持)
  - [5. 隐私净化与消除安全软件误报 (`a.gray.devicemaster.a`)](#5-隐私净化与消除安全软件误报-agraydevicemastera)
- [SMB 局域网共享连接指南](#smb-局域网共享连接指南)
- [从源码/脚本复现构建](#从源码脚本复现构建)
- [致谢与上游项目](#致谢与上游项目)

---

## 核心修复与升级一览

| 模块 | 原社区版痛点 | 本版本修复方案 |
| :--- | :--- | :--- |
| **SMB 协议栈** | 内置 2015 年的 `jcifs 1.3.x`，**仅支持已淘汰的 SMBv1**，无法连接默认禁用 SMBv1 的 Win10/11、macOS 及现代 NAS | 升级至 **`jcifs-ng 2.1.10`** + 精简版 BouncyCastle 密码学组件，原生支持 **SMBv1 / SMBv2 / SMBv3（2.02 ~ 3.1.1）** 自动协商，传输缓冲提升 4 倍（256 KB） |
| **后台状态保持** | 浏览 SMB 文件夹时切换应用或返回桌面，再切回快图会**重置回本地相册主页**（大目录下甚至直接崩溃重启） | 修复 `DocumentFolder`/`LocalFolder`/`MediaStoreFolder` 序列化全量文件列表触发的 **Android 7.0+ Binder 512 KB 限制 (`TransactionTooLargeException`)**，并修复 `z`/`as` 页面恢复优先级 |
| **本地与时刻搜索** | 点击顶栏搜索图标输入关键词后报错：`create failed: java.lang.SecurityException: Failed to find provider...` | 修复 `targetSdkVersion >= 26` 下 `CommonFolder` 对 `file:///search` 注册 `ContentObserver` 引发的系统权限拦截，并为特殊字符搜索增加 `Pattern.quote()` 兜底 |
| **64 位兼容与动图** | 部分社区版通过二进制硬改 `.so` 实现 64 位兼容，存在解码崩溃、扫描死循环、GIF/WebP 动图失效及 DEX 重复类冲突 | 移植 `QuickPic-Gallery-Mod-2` 的 **纯 Java `JniUtils` 64 位引擎**，支持全架构（ARM64/x86_64），恢复原版扫描器并清理 186 个重复云端类 |
| **隐私与报毒治理** | 安装时被国产 ROM 管家拦截报毒 `a.gray.devicemaster.a` / `a.gray.devucenaster.a`（猎豹时期遗留统计与内建更新器特征） | 彻底剥离 **298 个友盟统计 (`b.a.*`/`com.c.a.*`) 与自更新 (`com.alensw.updater.*`) 类**，移除安装未知应用与读取系统账号等高危权限，使用全新 RSA-3072 私钥签名，并提供独立包名版 |

---

## 安装包版本对比与下载

发布包提供两个功能完全一致的签名版本（均已 4 字节 `zipalign` 对齐并通过 v2/v3 签名校验，体积仅 **2.41 MB**）：

| 文件名 | 包名 (`applicationId`) | 适用场景 | SHA-256 校验值 |
| :--- | :--- | :--- | :--- |
| **`图库_修复版.apk`** | `com.alensw.PicFolder` | 兼容原版快图包名，适合无系统包名黑名单拦截的设备 | `a2e1eab7deb586b0c02c6059a276cbfa0a2159cc0022ad3a0c32044f434fda2e` |
| **`图库_修复版_独立包名.apk`** | `io.github.quickpic.gallery` | **推荐使用**：可与原版共存，且彻底避开部分手机管家对 `com.alensw.PicFolder` 包名的云端静态黑名单 | `31a9d5178a2bdabd5ddcc6cec7c7f429a0e24ebe0cd99111cbcbcb6C791a0cc0` |

---

## 技术原理与根因分析

### 1. 原生支持 SMBv1 / SMBv2 / SMBv3（最高 SMB 3.1.1）

- **问题根因**：原版快图使用混淆在 `a.a.*` ~ `a.e.*` 包下的 `jcifs 1.3.x`，仅实现了上古的 `SMB_COM_NEGOTIATE (SMBv1)`。Windows 10 (1709+)、Windows 11、macOS 以及群晖 DSM 7、威联通、飞牛 fnOS、TrueNAS 等现代系统出于安全原因默认禁用了 SMBv1，导致快图无法连接。
- **技术实现**（详见 [`build_smb2_upgrade.py`](build_smb2_upgrade.py)）：
  1. 移除旧版 157 个 `jcifs 1.3` 类（仅保留并改造 `a.d.j` 的 `smb://` URL 解析入口，确保与 `BasicAuthActivity` 100% 兼容）。
  2. 引入 **`jcifs-ng 2.1.10`**，并重写快图 SMB 驱动桥接层 `com.alensw.cloud.a.bu`（继承自 `com.alensw.cloud.a.bv`）：
     - 配置 `jcifs.smb.client.minVersion=SMB1` 至 `jcifs.smb.client.maxVersion=SMB311`，开启 DFS 支持（`dfs.disabled=false`），关闭 IPC 强制签名限制（`ipcSigningEnforced=false`），并复用全局 `BaseContext` 连接池。
     - 定制轻量级 `jcifs.util.Crypto` 与 `Smb2SigningDigest`，桥接 `MD4`（NTLM 认证）、`HmacSHA256`（SMB 2.x 签名）与 `AES-CMAC`（SMB 3.0 / 3.0.2 / 3.1.1 签名）。
     - 通过静态依赖闭包裁剪 BouncyCastle（从完整库的数千个类精简至仅 **287 个核心密码学类**），使整个 SMBv2/v3 升级仅增加约 **360 KB** 体积。
     - **SMB2/3 Guest 匿名登录修复**：`jcifs-ng` 默认将空密码的 `guest` 视为普通用户（`AuthenticationType.USER`），在 SMB2/3 下会因尝试校验会话签名而失败。我们在 `bu` 中自动识别空用户名或空密码的 `guest` 账号，显式切换为 `AuthenticationType.GUEST`。
     - **路径与性能优化**：修正 `jcifs-ng` 在 `listFiles()`、`mkdir()` 和递归 `delete()` 时要求目录 URL 必须以 `/` 结尾的规范；自动隐藏 `IPC$`、`C$`、`ADMIN$` 等管理共享；将流式读取与下载缓冲区从 `60 KB` 扩大至 **`256 KB`**。

### 2. 修复 SMB/云端目录切后台或锁屏后回到主页的问题

- **问题根因**：
  1. **Binder 缓冲区溢出 (`TransactionTooLargeException`)**：`DocumentFolder`（用于承载 SMB/云盘目录）、`LocalFolder` 与 `MediaStoreFolder` 在 `writeToParcel`（用于 `onSaveInstanceState` 保存页面状态）时，将当前目录下的 `n`（全部文件列表 `ArrayList`）逐一写入了 `Bundle`。在 Android 7.0+ 中，当文件夹内包含几百张图片时，`Bundle` 体积会轻易突破 Binder 事务限制（512 KB ~ 1 MB），导致切换应用时 Activity 在后台直接崩溃销毁，再次切回时只能冷启动回主页。
  2. **恢复状态被原始 `Intent` 覆盖**：在快图的云端目录视图 `com.alensw.ui.c.z.a(Bundle)` 与大图查看器 `com.alensw.ui.c.as.a(Bundle)` 中，代码先读取了 `this.E.getParcelableExtra("QuickPic.folder")`（初始进入时的根目录），只在 `this.y == null` 时才去读取 `savedInstanceState.getParcelable("current_folder")`。由于初始 `Intent` 中的 `QuickPic.folder` 永远不为 `null`，切后台重建时保存的当前子目录状态被直接丢弃，永远回退到根路径。
- **修复方案**（详见 [`apply_patches.py`](apply_patches.py)）：
  - 在 `DocumentFolder`、`LocalFolder`、`MediaStoreFolder` 的 `writeToParcel` 中仅写入目录元数据并将子文件数写为 `0`，将 `Bundle` 体积从数百 KB 降至 **< 200 字节**；恢复后由快图自身的异步列表刷新机制重新加载文件项。
  - 调整 `z.smali` 与 `as.smali` 的初始化顺序：**优先从 `savedInstanceState` 读取 `current_folder` / `current_uri`**，仅在无保存状态时才回退至初始 `Intent`。

### 3. 修复搜索功能崩溃 (`SecurityException: Failed to find provider`)

- **问题根因**：
  - 快图的搜索结果页面 `com.alensw.ui.c.dc`（继承自 `z`）通过创建虚拟目录 `new LocalFolder("/search", keyword, ...)` 来展示搜索结果，其 `i()` 方法返回的 URI 为 `file:///search`（`scheme` 为 `"file"`，`authority` 为空）。
  - 原版快图的 `targetSdkVersion` 为 `23`，而上游社区版将其修改为了 `34`。在 Android 8.0 (API 26)+ 中，当 `targetSdkVersion >= 26` 时，系统 `ContentService.registerContentObserver()` 强制校验 URI 的 `authority` 必须对应已注册的 `ContentProvider`，否则直接抛出 `java.lang.SecurityException: Failed to find provider  for user 0; expected to find a valid ContentProvider for this authority`，被 `cx.a()` 捕获后弹出 `create failed: java.lang.SecurityException...`。
- **修复方案**（详见 [`fix_search_bug.py`](fix_search_bug.py)）：
  - 在 `CommonFolder.a(ContentResolver, ContentObserver)` 中增加协议判断（仅当 `"content".equals(uri.getScheme())` 时才注册 `ContentObserver`）与 `try-catch` 保护。
  - 在 `aw.smali` 与 `bd.smali`（从搜索结果点开大图或删除图片时触发的 `notifyChange`）中增加异常保护。
  - 在搜索任务 `dd.smali` 中为 `Pattern.compile(keyword, CASE_INSENSITIVE)` 增加 `Pattern.quote(keyword)` 回退机制，防止搜索包含 `(`、`[`、`*`、`+` 等特殊字符的文件名时因 `PatternSyntaxException` 崩溃。

### 4. 纯 Java 64 位图像引擎与 GIF/WebP 动图支持

- 移除社区版通过 Hex 硬改字符串伪造的 64 位 `.so` 库，完整集成 [`jason840709/QuickPic-Gallery-Mod-2`](https://github.com/jason840709/QuickPic-Gallery-Mod-2) 的纯 Java `com.alensw.b.b.JniUtils` 实现。
- 恢复原版干净的媒体扫描器 `com.alensw.a.al`（移除上游硬编码的 `com.wstxda.gsl` 引用与空循环）。
- 清理多 DEX 合并时产生的 **186 个重复 `com.alensw.cloud.*` 类**，消除 ART 虚拟机类校验与方法内联冲突。

### 5. 隐私净化与消除安全软件误报 (`a.gray.devicemaster.a`)

- **彻底移除 298 个统计与自更新类**：
  - 删除 `b/a/*`（266 个友盟 Analytics SDK 类，包含读取 IMEI/MAC/安装列表并上传 `alog.umeng.com` 的代码）。
  - 删除 `com/c/a/*`（14 个友盟增量更新 SDK 类）与 `com/alensw/updater/*`（18 个静默下载安装 APK 的自更新类）。
  - 将 `com.alensw.b.f.a` 统计埋点桥接类替换为空实现（No-op）。
- **精简敏感权限**：从 `AndroidManifest.xml` 中移除 `REQUEST_INSTALL_PACKAGES`、`GET_ACCOUNTS`、`MANAGE_ACCOUNTS`、`USE_CREDENTIALS`、`AUTHENTICATE_ACCOUNTS`、`READ_SYNC_SETTINGS`。
- **全新私有签名与独立包名**：弃用全网泛滥的 AOSP `testkey` 公开测试证书，使用全新生成的 3072-bit RSA 证书进行 v2/v3 签名，并提供 `io.github.quickpic.gallery` 独立包名版。

---

## SMB 局域网共享连接指南

1. **启用云端服务入口**：
   - 打开快图 → 点击左上角 `☰` 侧边栏 → **设置** → **浏览** → 勾选 **「云端服务」**。
2. **添加 SMB 服务器**：
   - 打开侧边栏 → 点击 **「云端空间」** → 点击右上角 **`+` 号** → 选择底部的 **「Samba (局域网共享)」**。
   - **自动发现**：若处于同一局域网，快图会自动扫描并列出局域网内的电脑/NAS，直接点击即可填入地址。
   - **手动输入**：点击右上角编辑/电脑图标，在地址栏输入服务器 IP 或路径（例如 `192.168.1.100` 或 `192.168.1.100/Photos`）。
3. **支持的账号与登录格式**：
   - **普通账号**：用户名填 `你的用户名`，密码填 `你的密码`
   - **域账号（支持三种写法）**：`域名\用户名`、`域名;用户名` 或 `用户名@域名`
   - **匿名 / Guest 访问**：用户名留空（会自动填入 `guest`）且密码留空，即可使用原生 SMB2/3 Guest 会话登录

---

## 从源码/脚本复现构建

本仓库提供完整的自动化构建与补丁脚本，任何开发者均可在本地一键复现：

### 1. 环境依赖
- Python 3.9+
- OpenJDK 17 或 21
- Android SDK Build-Tools（`d8`、`zipalign`）
- `apktool` 2.9+ / 3.0+、`baksmali`、`uber-apk-signer`

### 2. 构建流程
```powershell
# 1. 应用基础修复补丁（SMB 后台状态保持、64 位纯 Java 引擎、去广告/统计与权限清理）
python apply_patches.py

# 2. 编译并注入 jcifs-ng 2.1.10 SMBv1/v2/v3 协议栈与裁剪后的 BouncyCastle 密码学包
python build_smb2_upgrade.py

# 3. 应用 Android 8.0+ 搜索崩溃 (SecurityException) 与正则容错补丁
python fix_search_bug.py

# 4. 生成独立包名版 (io.github.quickpic.gallery) 工程树
python build_standalone_pkg.py

# 5. 使用 apktool 打包、zipalign 对齐并签名
java -jar tools/bin/apktool.jar b -p tools/framework apktool_out -o build_unsigned.apk
tools/bin/zipalign.exe -f 4 build_unsigned.apk build_aligned.apk
tools/bin/uber-apk-signer.bat -a build_aligned.apk --ks release.jks --ksAlias release --ksPass <密码> --ksKeyPass <密码> --skipZipAlign
```

---

## 致谢与上游项目

- **原版快图 (QuickPic 4.5.2)**：Nanling Zheng (Alensw)
- **[WSTxda/QP-Gallery-Releases](https://github.com/WSTxda/QP-Gallery-Releases)**：现代 Android 适配基础版本
- **[hstonc/QP-Gallery-Releases-Mod](https://github.com/hstonc/QP-Gallery-Releases-Mod)**：高帧率与社区改进参考
- **[jason840709/QuickPic-Gallery-Mod-2](https://github.com/jason840709/QuickPic-Gallery-Mod-2)**：纯 Java 64 位 `JniUtils` 引擎与动图解码实现
- **[AgNO3/jcifs-ng](https://github.com/AgNO3/jcifs-ng)** & **[BouncyCastle](https://www.bouncycastle.org/)**：SMBv2/SMBv3 协议栈与加密支持

---

## 开源许可与合规声明 (License)

- 本仓库新增的自动化修补/构建脚本、桥接源码与文档采用 **[MIT License](LICENSE)** 开源。
- 第三方开源组件（`jcifs-ng` LGPL-2.1、`BouncyCastle` MIT、`QuickPic-Gallery-Mod-2` MIT）的合规声明与历史底包著作权说明详见 **[LICENSING.md](LICENSING.md)**。

