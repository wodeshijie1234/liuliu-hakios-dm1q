# 架构与启动契约

## 已确认

- 本机：SM-S9110 / dm1q / SM8550，CHC，Android 16。
- 当前引导版本 S9110ZCS8FZI1，设备报告 rollback 位 8。
- 三星使用 Download/Odin 路径。没有依据证明本机支持 POCO 教程里的 fastboot boot。
- HakiOS 设备表仅注册 qemu 和 redwood；SM8550 与 SC7280/SM7325 属不同 SoC 支持范围。
- Mu-Silicium 状态表有 S23+ dm2q，不能直接推导 dm1q 可用。

## 目标层次

原厂启动链 → 经本机验证的 dm1q UEFI/loader → XNU SM8550 最小平台 → 板级驱动 → 用户空间。
先输出日志，再显示和输入；存储写入应晚于内存、地址布局与退出机制验证。
引导存储布局、内存保留区、GIC、定时器、中断、显示地址、PMIC、UFS 与 USB 地址均需从源码和本机证据核对，不能复制猜测。

## 恢复前置条件

必须取得 SM-S9110 对应的原厂 BL/AP/CP/CSC 材料、来源和 SHA256，确认版本满足本机防回滚限制；确认本机可进入并退出 Download Mode，主机工具可检测本机。
分区名称清单不是分区内容备份。恢复官方固件不恢复 Knox 熔丝。
本工程的预检脚本不实施刷写，预检通过也不代表镜像已通过实机验证。
