# 当前状态

更新：2026-11-07，Asia/Shanghai。设备实测与固件下载证据采集于 2026-11-06 至 07 日。

**实机刷写阻塞：本机原厂启动链关闭正常 OEM 解锁入口。手机尚未解锁、清空或刷写；没有 XNU 实机启动和 HakiOS 驱动验证。**

用户目标仍为移植并开源 Galaxy S23 的 HakiOS。用户已接受清空和 Knox 后果，已同意 Git、本地任务跟踪及测试边界，无需重复索取这些授权。

## 已完成与证据边界

| 事项 | 当前结果 | 证据 |
|---|---|---|
| 设备身份 | SM-S9110 / dm1q / SM8550 / CHC；FZI1、rollback 8、board revision 14 | device-inventory.json、board-properties.json |
| 手机恢复正常使用 | 11月7日 00:12 再次 ADB 核对主用户 0、原版 FZI1、锁定、Knox=0；临时 USB 常亮为 0 | device-inventory-final.json；是采集时结果，不是持续监控 |
| 解锁入口 | 正常/维护模式均无确认页；精确设置 APK 与 ABL 门控解释该现象 | 解锁核查结论.md、oem-visibility-audit.json、abl-oem-gate-audit.json |
| 同代 BL 对照 | CHC 最早公开 B8/FZE3、TGY B8/FZI1 正常门控均返回 0 | earliest-b8-comparison.json、tgy-b8-comparison.json；未试刷 |
| 原厂恢复材料 | 完整同版 FZI1，BL/AP/CP/CSC/HOME_CSC 全部 ZIP CRC、附加 MD5 与 SHA256 已校验 | stock-recovery-verification.json；未做恢复刷写测试 |
| 精确板级树 | 实机选择 base DTB 0、DTBO 6；离线合并成功，修订范围 11..32 覆盖本机 14 | base-dtb-summary.json、dtbo-summary.json、merged-board-reference.json |
| 上游配置 | 固定 HakiOS 提交，生成 dm1q/sm8550，全部 25 个驱动关闭，cpus=1 | upstream-lock.json、devices/dm1q/；检查通过不等于平台实现 |
| UEFI 诊断程序 | AARCH64 EFI 编译、格式和哈希核验完成 | probe-build.json；未在手机执行 |
| 启动预检 | 完整恢复材料已消除恢复文件缺项；仍拒绝推进 | preflight-with-recovery.json：DM1Q_BOOT_CHAIN_NOT_VALIDATED |
| 开源 | 已创建公开仓库；研究资料与源码正在首次上传，无镜像发布 | README.md、THIRD_PARTY_NOTICES.md、Git 记录 |

## 存储与恢复材料

用户清理后实测约 57GiB（约 61GB）可用，空间阻塞已解除。下载和解析后最新 df 约 29GiB 可用，不能把最初 61GB 当作当前余量。

完整解密 ZIP 为 13,811,659,536 字节，SHA256：

```text
7cfe4cca0ea711e7371224e62fcfeed458ecf14b4f0a8c53792c0f8ed3fb5385
```

ZIP、五个 tar.md5、私有恢复 manifest、APK 和解析出的固件均在工程外的 work/，不入开源 Git。未展开 super/userdata，未取得设备私有分区备份。恢复包校验完成不代表恢复工具和实际回刷链路已验收。

## 新增的板级研究结果

- 官方 vendor_boot 的 base 0 与 DTBO 6 已合并，SHA256 d7daddc3aab38776fdb1350cb000f127d83a9547e2fe31cd10b89d2a74c54a29。这是静态树，未包含 ABL 运行时 fixup，不能冒充 live FDT。
- GIC 基址为 0x17100000 / 0x17180000，timer 19.2MHz；CPU capacity 分组为 3+4+1。不能复制 redwood 的四小核掩码。
- GPU 实读 Adreno740v2；树中有 STM SPI 触控、QCA6490 无线/蓝牙、Cirrus CS35L43 扬声器和 CS40L26A 振动、MAX77705。候选节点和静态 status 不构成 HakiOS 支持证明。
- 上游 soc-args.py 生成 12/16 参数。三个保留内存参数的“未找到”来自节点名不匹配，原厂树实际有对应区域。MPSS PAS 仍未知。
- IPA 工具固定加 0x40000，原厂树给出的 qcom,ipa-cfg-offset 为 0x140000。已记录差异，未激活任何生成的参数。详见 soc-extraction-review.json、驱动适配清单.md。

## 下一步依赖

1. 首要条件是适用于 SM-S9110、当前防回滚代际的可验证启动准入途径；现无可执行方案。再做长按、切维护模式、试最早 CHC B8 或港版 B8 都没有新依据。
2. 准入解决后先验收 dm1q UEFI、只读诊断输出和返回原系统，再启动 XNU。不能以修改菜单或补丁字节代替镜像签名准入。
3. 驱动按日志、中断/定时器、显示、输入、USB、存储等顺序逐项验收。短信与接码依赖蜂窝链路，当前完全没有可用性证据。
4. 用户指定 wodeshijie1234，已通过其 Chrome 登录创建公开仓库 liuliu-hakios-dm1q；本地 origin 已设置。首次上传完成后以远端文件树与本地 Git tree 比较确认交付，不包含固件或设备标识。

复现见 [原厂设备树复现.md](原厂设备树复现.md)。此前逐步探索记录保留在 [历史状态](history/2026-11-06-state-before-stock-verification.md)，其中的“等待/下载中/空间不足”是历史状态，不再作为当前结论。

最终本地检查记录见 [validation-final.json](validation-final.json)。4项测试、上游配置检查和设备树重合并通过；未进行独立实机验收，不放行刷写。
