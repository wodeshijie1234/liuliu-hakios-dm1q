# liuliu HakiOS dm1q bring-up

版本：0.1.0-dev。目标设备：Samsung Galaxy S23 SM-S9110 / dm1q / SM8550。

这是独立研究工程，目标是为 dm1q 建立可复现的 HakiOS 引导和设备支持。
**当前没有可刷镜像，没有 XNU 实机启动证据，没有已验证的 HakiOS 驱动。**
当前已完成设备身份与锁状态核查、完整原厂恢复包校验，以及精确原厂设备树的离线合并。
**SM-S9110 当前 B8 原厂启动链关闭正常 OEM 解锁入口，实机启动仍被阻塞。**
不能把 S23+ dm2q、S23 Ultra dm3q 或 POCO redwood 的镜像刷入本机。

代码署名：@liuliu。与 Samsung、Apple、HakiOS、Mu-Silicium 无隶属关系。
后续复用第三方源码时保留其许可证和署名；不分发 Apple 用户空间、手机固件或设备私有分区。

## 验收顺序

1. 固定上游提交；采集可公开硬件信息；准备本型号同等或更高防回滚版本的恢复材料。
2. 核实 OEM 解锁资格和 Download Mode 的真实状态。
3. 为 dm1q 建立 UEFI/loader 输出与可回收调试通道，先验收退出并返回原厂系统。
4. 启动 XNU 到首条日志，再依次接入定时器、中断、显示、输入、USB、存储和其他驱动。
5. 只有实机证据支持后，才提高支持状态和发布镜像。

运行记录见 [docs/project_state.md](docs/project_state.md)。
驱动差异与缺口见 [驱动适配清单](docs/驱动适配清单.md)，静态板级资料的复现见 [原厂设备树复现](docs/原厂设备树复现.md)。

## 已有代码与验证

- `scripts/preflight.py`：ADB 白名单采集与离线恢复材料预检，绝不执行解锁或刷写。
- `devices/dm1q/`：上游工具生成的初始设备层，全部驱动关闭，支持状态均为 missing；并非可启动移植。
- `src/uefi_probe.c`：UEFI 控制台诊断程序，只读取 CPU、GOP 和内存图，随后返回调用者。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/preflight.py --adb /path/to/adb --output docs/device-inventory.json
# 离线预检当前应拒绝推进，返回码 2：
python3 scripts/preflight.py --inventory docs/device-inventory.json --output docs/preflight-result.json
# 使用已校验的 Zig 0.14.1，只编译诊断程序：
ZIG=/path/to/zig sh scripts/build-probe.sh
```

EFI 程序不能当 Odin 固件或 Android boot.img 刷入。当前没有经过本机验证的 UEFI 来加载它。

## 本机解锁核查

截至 2026-11-06，正常和维护模式下均未完成解锁，Knox 仍为 0。长按超过 30 秒不产生确认页，已排除按键时长不足。
本机设置程序的 OEM 菜单谓词遇到 `ro.boot.other.locked=1` 即返回 false，本机属性正是 1。
详见 `docs/unlock-check.json` 和 `docs/oem-visibility-audit.json`。
精确原厂 ABL 的资格函数正常返回恒 0，调用方跳过长按处理；CHC 最早公开 B8/FZE3 与 TGY 同代 B8/FZI1 对照也保留该门控。未执行降级或跨区刷写。
这证明当前正常入口受阻，不能据此宣称全部研究路线永久不可行；目前未找到精确型号/引导代际可复现的正常解锁替代方案。

离线静态审计可重跑，脚本仅接受已核对过的精确 APK 哈希，不修改 APK 或手机：

```sh
# 独立环境中安装 dexparser==1.2.0；APK 从自己的手机只读取得，勿发布。
python3 scripts/audit_oem_visibility.py --apk /private/path/SecSettings.apk --output /private/path/audit.json
```

未知 APK 构建会返回码 2，避免把另一个固件的流程错认成本机结论。

完整恢复包留在本地私有工作目录，不随源码分发；其校验记录见 `docs/stock-recovery-verification.json`。恢复刷写未经实机验收。
公开仓库：https://github.com/wodeshijie1234/liuliu-hakios-dm1q 。
首次公开内容为研究资料与工具源码，没有刷机包或驱动可用性承诺。
