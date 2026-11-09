# 授权与合规说明 (Licensing & Compliance)

本项目的代码与发行包（Release APK）涉及以下三部分授权范围，特此声明以保障开源合规与原作者权益：

---

## 1. 本仓库新增脚本与适配代码（MIT License）

本仓库内的自动化修补与构建脚本（`apply_patches.py`、`build_smb2_upgrade.py`、`fix_search_bug.py`、`build_standalone_pkg.py`）、新增桥接代码（如重写后的 `com.alensw.cloud.a.bu`）以及文档（`README.md`、`RELEASE_NOTES.md` 等）采用 **[MIT License](LICENSE)** 开源。

> **注意**：MIT 许可证仅涵盖本仓库公开的新增脚本、补丁代码及文档，**不会**将构建所用的基础 APK 或历史快图（QuickPic）原始二进制代码重新授权为 MIT。

---

## 2. 第三方开源组件合规声明（Third-Party Open Source Libraries）

为了实现 **SMBv2 / SMBv3 (2.02 ~ 3.1.1)** 协议栈升级与纯 Java 64 位渲染兼容，构建脚本引入并集成了以下开源组件，并严格遵守其各自的开源许可证：

| 组件名称 | 版本 | 许可证 | 源码与修改公开说明 |
| :--- | :--- | :--- | :--- |
| **[AgNO3/jcifs-ng](https://github.com/AgNO3/jcifs-ng)** | `2.1.10` | **LGPL-2.1** | 为适配 Android 系统内置 JCE Provider（Conscrypt），我们对 `jcifs.util.Crypto` 与 `jcifs.smb.Smb2SigningDigest` 进行了免外部 Provider 依赖修改。**根据 LGPL-2.1 许可证要求，修改后的完整 Java 源代码已在 [`build_smb2_upgrade.py`](build_smb2_upgrade.py) 中完全公开**，任何人均可通过该脚本替换或重新链接 `jcifs-ng` 版本。 |
| **[BouncyCastle (`bcprov-jdk18on`)](https://www.bouncycastle.org/licence.html)** | `1.78.1` | **MIT License** | 仅提取并保留 `jcifs-ng` 所需的 `org.bouncycastle.asn1.*`、`crypto.*`、`math.*`、`util.*` 子集，用于 SPNEGO ASN.1 与 MD4/RC4/CMAC 基础算法计算。 |
| **[SLF4J (`slf4j-api` / `slf4j-nop`)](https://www.slf4j.org/license.html)** | `1.7.36` | **MIT License** | 用于承接 `jcifs-ng` 的日志接口调用。 |
| **[QuickPic-Gallery-Mod-2](https://github.com/jason840709/QuickPic-Gallery-Mod-2)** | `11.0.0` | **MIT License** | 集成 Jason Chen 编写的纯 Java 64 位 `com.alensw.bean.JniUtils` 引擎及动图（WebP/GIF）兼容补丁，著作权归原作者 Jason Chen 所有。 |

---

## 3. 历史快图（QuickPic）底包与免责声明

1. **原始著作权归属**：快图浏览（QuickPic `4.5.2`）原始应用程序的设计、图标及历史代码著作权归原作者 **Nanling Zheng (Alensw)** 所有；后续 Android 兼容性维护参考了 [WSTxda/QP-Gallery-Releases](https://github.com/WSTxda/QP-Gallery-Releases) 与 [hstonc/QP-Gallery-Releases-Mod](https://github.com/hstonc/QP-Gallery-Releases-Mod)。
2. **仓库不托管闭源底包**：这也是本 Git 仓库默认**仅托管补丁脚本而不直接上传完整反编译源码树（`apktool_out/`）**的重要原因之一——将新增的开源补丁与历史专有代码明确分离。
3. **非商业学习用途**：本项目及附带的构建产物完全免费、无任何内购或商业盈利行为，仅用于个人技术研究、安全隐私净化（移除已废弃的第三方统计/自升级 SDK）以及现代 NAS（SMBv2/v3）兼容性修复。如有侵权或权利人异议，请联系仓库维护者移除相关二进制构建物。
