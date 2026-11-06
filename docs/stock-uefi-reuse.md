# 精确原厂UEFI组件研究

本机FZI1 BL已通过ZIP CRC、附加MD5和独立samloader校验，固件留在work，不分发。
解析出的ABL/UEFI共111个PE段、108个唯一哈希（包含嵌套容器造成的重复项），模块名与哈希见module-catalog.json。

## 可作为板级移植依据

已取得本机版本的DisplayDxe、ButtonsDxe、UsbPwrCtrlDxe、UsbfnDwc3Dxe、UsbDeviceDxe、UsbConfigDxe、UsbInitDxe、UFS相关组件和嵌入的内存配置。
这些是UEFI固件模块，不是XNU驱动；存在文件不代表能够直接在自定义UEFI或XNU中使用。

嵌入配置的UEFI FD区域为0xA7000000/0x400000；Mu-Silicium的dm2q移植将其中部分切给自定义FD。该切分不能在dm1q未经验证直接沿用。

xbl_config与uefi.elf的嵌入配置在PIL、TZApps保留区等有差异。当前保留两份来源记录，等待实际UEFI内存图；不擅自合并猜测。

## 精确板级选择

ADB读到revision=14、dtb_idx=0、dtbo_idx=6、平台kalama，GPU实读Adreno740v2。
从已完成下载块提取的精确FZI1 dtbo中index6标为board-id11、适用hw_rev 11到32，覆盖本机14。
完整 AP 的 ZIP CRC/附加 MD5 已校验，重新提取的 boot/dtbo 与先前暂存结果 SHA256 完全相同。详见 provisional-recheck.json、dtbo-summary.json；原始 dtbo 不入库。
官方 vendor_boot 的 base0 与该 overlay6 已用 libfdt 合并成功，见 merged-board-reference.json。静态树不含启动时 fixup。

## 防回滚代际对照

已只下载CHC最早公开B8版本FZE3的BL，CRC/MD5通过；其LinuxLoader在同一门控位置仍固定返回0，并含other.locked=1字面量。
因此至少“回退CHC最早B8即可恢复正常解锁入口”没有依据。后续 TGY 同代 B8/FZI1 也做过独立文件校验和门控对照，结果同样返回0；未刷机试验，不外推所有未检查固件。
