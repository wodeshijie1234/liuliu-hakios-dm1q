# Third-party notices

`devices/dm1q` 的初始结构由 HakiOS 的 `tools/hakios-device.py new` 生成，随后关闭全部硬件与虚拟驱动，并将状态改为未经实机验证。`third_party/hakios/efi.h` 原样取自同一提交的 `xnuloader/efi.h`，遵守下列 MIT 许可。

Upstream: https://github.com/oosexgang/hakios-xnu-kernel
Commit: 63fc2b4633bac3af8e57dadab9f5a8d4cb940438

MIT License

Copyright (c) 2025-2026 the HakiOS authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Mu-Silicium 的 dm2q 源码目前仅在工作目录中审阅，未复制为本机实现。
本工程未分发上游二进制、厂商固件、Apple 用户空间或设备私有数据。
