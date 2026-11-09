# GitHub Release 发布说明 & 上游 PR 提交模板

本文档包含两部分：
1. **GitHub Release 发布文案**：可直接复制到你自己仓库的 GitHub Releases 页面，并上传两个编译好的 `.apk` 附件。
2. **上游 Issue / Pull Request 提交文案（中英双语）**：可直接提交至 `WSTxda/QP-Gallery-Releases`、`hstonc/QP-Gallery-Releases-Mod` 或 `jason840709/QuickPic-Gallery-Mod-2`，帮助上游社区合并修复。

---

## 一、GitHub Release 发布文案（直接复制使用）

### 标题
`v10.0-SMBv3-Fix: 原生支持 SMBv1/v2/v3 (3.1.1)、修复 SMB 切后台重置、修复搜索崩溃与误报毒`

### 正文

#### 核心更新亮点

1. **原生支持 SMBv1 / SMBv2 / SMBv3（最高 SMB 3.1.1）**
   - 移除老旧仅支持 SMBv1 的 `jcifs 1.3.x`，升级为 **`jcifs-ng 2.1.10`** 并重写 `com.alensw.cloud.a.bu` 驱动层。
   - 无需在电脑或 NAS 开启已淘汰的 SMBv1，即可直接连接 **Windows 10/11、macOS、群晖 DSM 7、威联通、飞牛 fnOS、TrueNAS、Unraid**。
   - 支持普通账号、域账号（`domain\user` / `domain;user` / `user@domain`）及 **SMB2/3 原生 Guest 匿名登录**。
   - 全局共享连接池，流式读取与下载缓冲从 `60 KB` 提升至 **`256 KB`**；按依赖闭包裁剪 BouncyCastle，APK 体积仅增加约 `360 KB`。

2. **修复浏览 SMB/云盘文件夹切后台或回桌面后回到主页的问题**
   - 修复 `DocumentFolder`、`LocalFolder`、`MediaStoreFolder` 在 `writeToParcel` 时将全部子文件写入 `Bundle` 导致触发 **Android 7.0+ Binder 512 KB 限制 (`TransactionTooLargeException`)** 的崩溃问题。
   - 修复 `com.alensw.ui.c.z` 与 `com.alensw.ui.c.as` 页面重建时原始 `Intent` 覆盖 `savedInstanceState`（`current_folder` / `current_uri`）的逻辑缺陷。

3. **修复高版本 Android 搜索报错 (`create failed: java.lang.SecurityException`)**
   - 修复 `targetSdkVersion >= 26` 下 `CommonFolder` 对搜索虚拟路径 `file:///search` 注册 `ContentObserver` 引发的 `SecurityException: Failed to find provider` 崩溃。
   - 修复从搜索结果查看或删除图片时 `notifyChange(file:///search)` 的异常。
   - 为搜索关键词正则编译增加 `Pattern.quote()` 兜底，支持搜索包含 `(`、`[`、`*`、`+` 等特殊字符的文件名。

4. **纯 Java 64 位引擎与动图修复**
   - 采用 `QuickPic-Gallery-Mod-2` 的纯 Java `JniUtils` 64 位实现，全架构通吃（ARM64/x86_64），完美支持 GIF 与动态 WebP。
   - 恢复原版干净的 `al.smali` 扫描器，移除 186 个跨 DEX 重复云端类。

5. **彻底剥离友盟统计与自更新模块，解决杀毒软件误报 (`a.gray.devicemaster.a`)**
   - 移除 298 个友盟统计 SDK（`b.a.*`、`com.c.a.*`）与内建自更新器（`com.alensw.updater.*`）类，剔除安装未知应用、读取系统账户等敏感权限。
   - 使用全新生成的 3072-bit RSA 私钥进行 v2/v3 签名，并提供独立包名共存版。

#### 下载说明与校验值

| 安装包 | 包名 | 说明 | SHA-256 |
| :--- | :--- | :--- | :--- |
| **`图库_修复版.apk`** | `com.alensw.PicFolder` | 原包名覆盖/替换版（`2.41 MB`） | `a2e1eab7deb586b0c02c6059a276cbfa0a2159cc0022ad3a0c32044f434fda2e` |
| **`图库_修复版_独立包名.apk`** | `io.github.quickpic.gallery` | **推荐**：独立包名共存版，彻底规避手机管家对原包名的云端黑名单（`2.41 MB`） | `31a9d5178a2bdabd5ddcc6cec7c7f429a0e24ebe0cd99111cbcbcb6c791a0cc0` |

---

## 二、向上游仓库提交 Issue / PR 的模板（中英双语）

### Title
`[Patch/Fix] Upgrade SMB to SMBv2/v3 (jcifs-ng), fix SMB background state reset, fix Search SecurityException on targetSdk>=26, and strip Umeng SDK`

### Description (English / 中文)

#### Summary (概述)
We have identified and fixed several critical issues in the current QuickPic Gallery Mod builds when running on modern Android (Android 8.0 ~ 16, `targetSdkVersion >= 26`), and upgraded the built-in SMB client to support **SMBv1 / SMBv2 / SMBv3 (up to SMB 3.1.1)**.

我们在现代 Android 系统（Android 8.0 ~ 16，`targetSdkVersion >= 26`）下定位并修复了当前快图修改版的多个关键问题，并将内置 SMB 客户端升级为原生支持 **SMBv1 / SMBv2 / SMBv3（最高 SMB 3.1.1）**。

---

#### 1. Native SMBv1 / SMBv2 / SMBv3 (3.1.1) Support via `jcifs-ng 2.1.10`
- **Problem**: The legacy `jcifs 1.3.x` (`a.a.*` ~ `a.e.*`) only supports SMBv1, which is disabled by default on Windows 10/11, macOS, and modern NAS systems.
- **Fix**:
  - Replaced `jcifs 1.3.x` with `jcifs-ng 2.1.10` and rewrote `com.alensw.cloud.a.bu` (extending `com.alensw.cloud.a.bv`).
  - Implemented custom `jcifs.util.Crypto` (`MD4` + `AES-CMAC`) and `Smb2SigningDigest` backed by a tree-shaken BouncyCastle closure (only 287 classes, adding just ~360 KB to the APK).
  - Added proper SMB2/3 `AuthenticationType.GUEST` handling for guest logins, trailing `/` normalization on directory operations (`listFiles`, `mkdir`, recursive `delete`), shared `BaseContext` connection pooling, and a 256 KB streaming buffer.

#### 2. Fix SMB/Cloud Folder State Reset When Switching Apps (`TransactionTooLargeException` & Intent Override)
- **Problem**: When browsing an SMB folder and switching to another app or returning to the home screen, reopening QuickPic resets back to the main local gallery screen.
- **Root Cause**:
  1. `DocumentFolder.writeToParcel` (as well as `LocalFolder` and `MediaStoreFolder`) serializes the entire child file list (`this.n`) into the `savedInstanceState` `Bundle`. On Android 7.0+, folders with hundreds of files exceed the 512 KB Binder transaction limit (`TransactionTooLargeException`), killing the backgrounded Activity.
  2. In `com.alensw.ui.c.z.a(Bundle)` and `com.alensw.ui.c.as.a(Bundle)`, `this.E.getParcelableExtra("QuickPic.folder")` (the initial root folder) is read *before* `savedInstanceState.getParcelable("current_folder")`, so the saved subfolder is always ignored on recreation.
- **Fix**:
  - Write `0` child items in `writeToParcel` for `DocumentFolder`, `LocalFolder`, and `MediaStoreFolder` so the saved `Bundle` stays under 200 bytes.
  - Prioritize `savedInstanceState.getParcelable("current_folder")` / `"current_uri"` over `this.E` in `z.smali` and `as.smali`.

#### 3. Fix Search Crash (`create failed: java.lang.SecurityException: Failed to find provider`)
- **Problem**: Searching in the gallery throws `create failed: java.lang.SecurityException: Failed to find provider  for user 0; expected to find a valid ContentProvider for this authority`.
- **Root Cause**: `com.alensw.ui.c.dc` creates a virtual `LocalFolder("/search", keyword, ...)` whose `i()` returns `file:///search`. When `targetSdkVersion >= 26`, Android's `ContentService.registerContentObserver()` rejects non-`content://` URIs with a `SecurityException`.
- **Fix**:
  - Guard `CommonFolder.a(ContentResolver, ContentObserver)` so `registerContentObserver` is only called when `"content".equals(uri.getScheme())` inside a `try-catch` block.
  - Guard `notifyChange` in `aw.smali` and `bd.smali` when viewing/deleting items from search results.
  - Add a `Pattern.quote()` fallback in `dd.smali` when compiling regex search patterns so special characters (`[`, `(`, `*`, `+`) do not throw `PatternSyntaxException`.

#### 4. Remove Umeng Analytics & Self-Updater (`a.gray.devicemaster.a` False Positive)
- Removed 298 classes in `b/a/*` (Umeng Analytics), `com/c/a/*` (Umeng Update), and `com/alensw/updater/*`, stubbed `com.alensw.b.f.a`, and stripped `REQUEST_INSTALL_PACKAGES` and account permissions from `AndroidManifest.xml`.
