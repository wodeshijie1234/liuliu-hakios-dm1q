# 历史状态：完整恢复包校验前

此文件保留探索过程中的旧状态，不代表当前进展。当前结论以 ../project_state.md 为准；其中“待下载、空间不足、等待用户、ADB未复核”等状态后续已更新。

记录时间：2026-11-06，Asia/Shanghai。

目标：为用户的备用 Galaxy S23 建立 HakiOS 移植并开源给同型号用户。
用户已明确接受清空约 213GB 现有数据和 Knox 永久后果。
用户已同意建立 AGENTS.md、本地任务跟踪和隐私/机型/恢复材料测试边界。

## 实机证据

- ADB 授权连接成功，SM-S9110 / dm1q / SM8550 / CHC。
- S9110ZCS8FZI1，Android 16，One UI 属性 80500，安全补丁 2026-08-05。
- flash.locked=1，vbmeta.device_state=locked，verifiedbootstate=green。
- warranty_bit=0，ro.boot.rp=8。
- oem_lock 服务存在，但 shell 不提供查询命令；OEM 解锁允许属性为空，不能由此断言无法解锁。
- 可列出分区名称，但 boot/init_boot/recovery/vendor_boot/dtbo/vbmeta 块设备仅 root 可读。
- /sys/firmware/fdt 与 live device tree 正文对 shell 拒绝访问。
- 尚未取得私有分区备份或原厂恢复包。

## 主机证据

- Mac 系统盘可用约 11GB；完整固件和构建空间需要单独安排。
- GitHub Git clone 本次超时；raw.githubusercontent.com 可读。
- 当前尚未构建镜像、解锁或写入任何手机分区。

## 公开资料

- https://github.com/oosexgang/hakios-xnu-kernel
- https://github.com/oosexgang/hakios-xnu-kernel/blob/main/docs/porting/index.md
- https://github.com/Project-Silicium/Mu-Silicium/blob/main/Status.md
- https://github.com/topjohnwu/Magisk/blob/master/docs/install.md
- https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/hw-backed-security/

后续动作：核实手机解锁入口，取得并审阅固定上游源码，建立可重跑的只读采集与离线预检。

## 本轮新增证据

- HakiOS 固定提交 `63fc2b4633bac3af8e57dadab9f5a8d4cb940438` 的官方源码包已下载；879 个文件逐个与 Git blob SHA1 核对一致，归档 SHA256 见 upstream-lock.json。
- 已用上游 `hakios-device.py new` 生成 dm1q / sm8550 结构，并手动收紧配置：全部 25 个硬件/虚拟驱动关闭，固件 none，只保留 cpus=1。
- 上游 device check 与 config check 通过，尚未编译 XNU 或在本机运行。
- 上游 loader 当前只定义 qemu-virt 和 redwood，并通过 framebuffer 地址选择，新增配置不会自动提供 dm1q 引导。
- 隐私白名单、同 SoC 异机型拒绝、恢复文件缺失和空口声称恢复可用等 4 项离线测试通过。实际预检 ready=false。
- 用户照片确认 ADB reboot download 到达的画面只有中央下载提示；退出后重新 ADB 采集，bootloader、锁状态、Knox 位均未变（Knox=0）。
- 用户从正常关机后双音量键插线进入的警告页，照片底部中文明确显示“长按音量增加键：设备解锁模式”。这验证了解锁模式入口存在，尚未证明最终 OEM 解锁成功。
- 当前等待进入设备解锁模式的确认页照片。

本轮没有刷写镜像、没有备份分区内容、没有发布 GitHub 仓库。数据清空尚未执行。

## 当前接力点

- 用户确认 Warning 页连续按音量上超过 30 秒，按下瞬间进入 Download Mode，无解锁确认页。不是按键时长不足，不再要求重复。
- 实机 `ro.boot.other.locked=1`。用户已再次正常退出 Download Mode。
- 国行维护模式正常入口已经找到：智能管理器 → 实用工具 → 向下滚动 → 更多关注 → 维护模式。
- 点击开启后提示“请先设置屏幕锁定”。当前等待用户自行设置临时锁屏并开启；不收集 PIN/密码。
- 当前 ADB 仍为普通用户，维护模式尚未确认开启。
- 系统已有本地代理，命令只临时指定当前本地 HTTP 代理后，GitHub 与 PyPI 下载成功；没有修改全局代理。
- `src/uefi_probe.c` 已编译为 135168 字节 AARCH64 PE32+ EFI 应用，无导入表；哈希见 probe-build.json。尚无设备运行证据。
- 精确 CHC/FZI1 官方恢复包元数据已查到：13811659552 字节（约 13.81GB）。未下载完整包，当前主机约 13GiB 可用，等待存储安排。
- FUS 已查询 CHC、TGY、BRI 的公开历史版本，没有找到同型号 binary 8 的 Android 15 候选；不可拿 S911B 的降级经验套用。
- 正常解锁核验受阻，UEFI 板级配置、XNU 及驱动尚未完成；不得声明首个移植成功。

用户最新约束：先完成解锁核查，再安排空间；暂不下载完整固件或进行大体积构建。

## 解锁资格的本机代码证据

- 维护模式已启动，ADB 当前用户=77。此模式下仍为 other.locked=1 / flash.locked=1 / vbmeta locked / warranty_bit=0。
- 只读拉取本机 `/system/priv-app/SecSettings/SecSettings.apk`，SHA256 为 `2ac6a07687b627a04615d9d2eb3e9c461b334ce5c81f426adcbbed817c0f5bcd`。
- 对其 `classes.dex` 的 `OemUnlockPreferenceController.isAvailable()` 做指令边界解码：若 `ro.boot.other.locked` 字符串等于 `1`，直接跳到返回 false。审计输出见 oem-visibility-audit.json。
- 这证实本机 OEM 菜单隐藏原因，不能单靠此方法外推引导器的全部内部逻辑，也不证明修改菜单能解锁。
- 未修改 APK、系统属性、引导器或任何锁标志。
- 当前等待维护模式下通过实体组合键进入 Download Mode 的状态照片。ADB 暂离线，符合用户正在切换模式的状态，未据此判定失败。

## 维护模式核验结果

用户已提供维护模式下的 Download Mode 照片：Samsung Official，KG CHECKING(00)，WARRANTY VOID 0x0，Secureboot/Download ENABLE，RP SWREV B8/K8/S8；仍无 OEM LOCK、FRP LOCK 字段。未保存照片、DID 或序列号。
正常与维护模式都没有可执行的解锁确认路径。当前结论为正常 OEM 解锁受阻，未找到本机本代可复现替代路线；不下结论“永久不可能”。
三星官方更新与跨区历史未提供恢复解锁证明；Samsung Developer FAQ 未提供消费者设备解锁授权申请接口。
当前等待用户退出 Download Mode 和维护模式，之后以 ADB 用户 0、锁状态和 Knox 再核对恢复。

已把可重跑的离线审计 CLI 收入 scripts/audit_oem_visibility.py，固定支持本次精确 APK 哈希；APK 和第三方固件未入库。

## 用户退出维护模式后的状态

用户已报告退出维护模式；USB 可见 Samsung Android，但暂时没有 ADB 接口（设备列表为空）。当前等待用户在主系统重新开启 USB 调试。尚未据此宣称主用户和锁状态完成复核，临时 stay_on 设置也尚未恢复验证。

固件范围请求首次因 URL 路径编码错误返回404，改为上游的原样路径后已成功读取 ZIP/ZIP64 目录，仅取约263KB。BL成员约102MB压缩；正在仅下载本机精确版本BL做静态审计，不下载完整AP，不写手机。完整恢复包仍未就绪。

BL范围下载过程中遇到会话401和服务503，已沿用上游的nonce刷新逻辑并加入有限重试、分块缓存。没有将部分文件视为校验通过；最终须ZIP CRC、附加MD5和SHA256全部记录。

## 精确 BL 的只读静态审计

仅从官方FUS范围下载BL成员：压缩102360050字节，解压tar123054193字节；ZIP CRC和附加MD5通过，另经samloader verify-md5验证。SHA256 `7e2279084532588d5c33169b0d45cf953d35547cc2c55f156afa3980f926d821`。BL二进制留在work，不入开源目录。

解压其abl.elf并解析UEFI固件卷，某主模块SHA256 `5943b3cb503dd53aec10aecb559911f31badc40df88636eb2ad5023a24cf0ac2` 含 ` androidboot.other.locked=1`。AArch64静态指令在RVA 0x5b6a0/0x5b6a4构造该字符串地址，并在0x5b6ac调用后续处理。记录见abl-other-locked-xrefs.json。

该证据确认本机精确版本引导模块有此字面量及引用，和Android属性、菜单隐藏逻辑一致；尚未完成全控制流/可信执行环境分析，不能宣称已经找到可解锁补丁。

## ABL 正常解锁界面的门控结论

精确ABL主模块静态审计：RVA 0xcac60 函数读取状态并可能打印 `[OEM]LOCK:%d`，但唯一正常返回路径在0xcacc4执行 `mov w0,wzr` 后ret，因此正常返回恒为0。Warning处理在0x707c8调用该函数，0x707d0跳至另一显示路径；在0x70810再次调用，0x70818按0跳过长按检测与0x7085c的解锁界面调用。明细见abl-oem-gate-audit.json。

该证据和“按下即进入Download、无长按确认”、Android other.locked=1、OEM菜单隐藏三者互相印证。结论限定为这版原厂ABL的正常解锁入口已关闭；不是所有代码已删除，也不是证明所有未来研究不可能。

不能通过复制dm2q镜像或仅修改Android菜单完成解锁。当前没有可在本机执行的已验证解锁路线；未生成或刷入ABL补丁。必须先解决签名启动链准入，才有条件运行UEFI/XNU实机适配。

用户已报告退出维护模式并重新插线；最新主机仍只有USB Samsung设备，无ADB设备。主用户返回、锁状态与临时亮屏设置尚待ADB复核；不把口头报告当作主机实测。

## 最新设备与空间复核

用户已重新开启调试；ADB已复核主用户0、SM-S9110/dm1q、同版FZI1、引导锁定、other.locked=1、Knox=0。临时USB常亮已恢复0。device-restored.json为当前证据，取代此前待复核记录。
用户清理空间后本机df实测57GiB可用（约61GB十进制），空间条件已解决。开始只下载精确同版FZI1完整原厂包并做恢复/设备树准备，仍不写手机。

## 原厂包下载与同代对照

完整FZI1包正在下载（可续传），当前空间57GiB足够恢复材料和本轮解析，仍不写手机。
只读下载并核验最早CHC B8版本FZE3的BL后，LinuxLoader在同一0xcac60门控位置也固定返回0，含other.locked=1。说明回退CHC最早公开B8不能据此恢复正常入口。详见earliest-b8-comparison.json。
已解出FZI1 ABL/UEFI的111个PE段（108个唯一哈希）及两份嵌入内存配置，原始固件留work，仅公开模块名/哈希/地址摘要。
从已标记下载完成的AP前部暂存提取boot/dtbo，待完整ZIP CRC和AP附加MD5后再升级证据。DTBO索引6的hw_rev范围11..32覆盖本机14；ADB实读GPU Adreno740v2。

港版TGY同代FZI1的BL也经CRC/MD5校验；LinuxLoader同位置0xcac60仍固定返回0，并含other.locked=1。详见tgy-b8-comparison.json；未执行跨区刷写。
完整原厂包下载后将做全部ZIP成员CRC、tar.md5和SHA256验证，再提取小型boot资产；尚未展开super系统镜像。
