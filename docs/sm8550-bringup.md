# SM8550 与 dm1q 启动差异

此处只记录静态源码证据；均未在本机用自定义代码验证。

## 中断与计时器

LineageOS 设备树固定提交 `5d524a80f98cabb136fdf360de501bed9ef13b06` 的 `qcom/kalama.dtsi`：

- GIC distributor: `0x17100000`，长度 `0x10000`。
- GIC redistributor: `0x17180000`，长度 `0x200000`，stride `0x40000`。
- 架构计时器 frequency：`19200000`；虚拟计时器为 PPI 11（GIC ID 27）。

Mu-Silicium 固定提交 `8471e47f5248ebbffc2e6196b683204163efe155` 的 `KailuaPkg.dsc.inc` 独立列出相同 GIC 基址，使用虚拟计时器。
这些地址与 HakiOS redwood 的 `0x17A00000 / 0x17A60000` 不同。不能复制 redwood 平台描述。
完整原厂包现已按实机选择合并 base0+overlay6，静态树给出 CPU capacity 820/1800/1894 三组，数量 3/4/1、MPIDR 0x0..0x700，启用方式 PSCI。不能复制 redwood 的四小核掩码。
该树不含启动时 fixup；framebuffer、运行时保留内存与 UEFI 实际布局仍需诊断输出。

## 上游 loader 的缺口

`xnuloader/loader.c` 只定义 `platform_qemu_virt` 和 `platform_redwood`。`efi_main` 默认选择 QEMU，仅在 GOP framebuffer base 为 `0xE1000000` 时改选 redwood。
未匹配的实体手机不会自动获得正确平台，因此不能直接运行上游 loader。
其中 payload 的固定位置和默认 logdump 日志写入也必须审查，不能把“RAM 运行”解释成完全不写手机。

当前采用独立 `src/uefi_probe.c`：读取 CPU 身份、GOP、UEFI 内存描述符并输出到 UEFI 控制台，不启动 XNU、不访问块设备或变量存储，不请求重启；输出后返回调用者。
该程序编译成 EFI 应用，依赖已验证的 UEFI；不能当 Android boot.img 或 Odin 固件刷入。

## 板级来源

LineageOS 有独立 dm1q 与 dm2q 的 European overlay，按板修订区分，不是本机 CHC/FZI1 的精确 FDT。
同一 overlay 会包含多种面板候选，不能从搜索到的首个面板名认定实际面板。
dm2q 的 UEFI 布局、固件二进制、DTB 均只能作参考。

## 当前解锁问题

实机 `ro.boot.other.locked=1`，Bootloader locked，Knox=0；开发者选项没有 OEM unlocking。
用户从 Warning 页持续按住音量上超过 30 秒，按下瞬间进入 Download Mode，无确认页；已排除时长不足。
警告页底部仍印有“设备解锁模式”，这只是可见文案，不是最终资格证明。
维护模式核查已完成，结果仍锁定；随后已退出并由 ADB 确认主用户0、Knox=0。维护模式不构成解锁权限授予。
官方与 FUS 历史未找到同型号 binary 8 的 Android 15，不能使用别的型号/更低防回滚版本试刷。

## OEM 菜单隐藏的精确固件证据

只读从本机取得 SecSettings.apk（SHA256 见 `oem-visibility-audit.json`），对 `classes.dex` 中 `OemUnlockPreferenceController.isAvailable()` 做指令边界解码。

相关分支：

```text
52  SystemProperties.get("ro.boot.other.locked")
58  String.equals("1")
61  move-result v0
62  if-nez v0, @81
...
81  return v1  # v1 先前设为 0
```

本机正常和维护模式均读取到该属性=1。因此该方法返回 false，解释 OEM 菜单隐藏。
同一方法还检查 FRP 分区属性、KnoxGuard 的 shouldBlockCustomRom 以及 OemLockManager 是否存在；这些检查不能混成单一 KG 结论。
上述 APK 静态审计没有写入手机、没有改变属性或菜单；它本身不证明 Bootloader 准入。
后续精确 ABL 审计确认正常 OEM 界面资格函数返回 0，详见 `abl-oem-gate-audit.json`；当前、CHC 最早 B8 和 TGY 同代 B8 的正常门控都受阻。

## 上游提取工具的 SM8550 假设

`soc-args.py:132` 将 IPA region 固定加 0x40000。本机静态树却有 `qcom,ipa-cfg-offset=0x140000`，且上游 IPA 驱动按参考机的 IPA 4.11 布局实现。不能只改一个地址就声称支持。
工具按精确叶名查找 cmd_db、mpss、ipa_gsi，本机分别命名为 aop_cmd_db_region、mpss_region、ipa_gsi_region，导致“未找到”。其中 mpss 节点名后缀为 0x89800000，而 `reg` 实值为 0x8a800000，必须读属性，不能照抄节点名地址。
这些仅记录在 `soc-extraction-review.json`，没有加入活跃启动参数或打开驱动。
