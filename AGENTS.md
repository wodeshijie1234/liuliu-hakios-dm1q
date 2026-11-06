# 项目边界

本工程为 liuliu 的 Galaxy S23 dm1q HakiOS 研究移植。中文记录，代码标识保留英文。
先读 docs/project_state.md 和 docs/architecture.md，再检查 Git 状态与活动任务。
不将其他机型镜像或主板地址冒充 dm1q；未知参数保持未知。
未观察到的启动和驱动能力必须记为未验证。
设备序列号、IMEI、电话号码、短信、账号和私有分区不得入库或发布。
不要因需要 root 而先写入未验证镜像；不要尝试账号锁或设备管理锁绕过。
用户已接受本机清空及 Knox 后果，该授权不替代镜像、机型和恢复材料校验。

## Agent skills

### Issue tracker

先用本地 Markdown，在 docs/task_list.md 跟踪阶段任务。尚无 GitHub remote。

### Domain docs

单一上下文；按需维护 GLOSSARY.md 和 docs/adr/。既有技术决定见 docs/architecture.md。

### 测试边界

用户已同意：测试采集接口的隐私白名单、机型不匹配和恢复材料缺失时拒绝推进。
实际启动与驱动另以实机日志验收；模拟数据和离线测试不能升级为设备支持。
