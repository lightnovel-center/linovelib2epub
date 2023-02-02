# console log alternatives

- [x] tqdm
  - 采纳，简洁好用，轻便。
- [ ] terminaltables
  - 感觉不如rich
- [x] tabulate
  - 非常简洁的表格显示，追求轻量可以使用。
- [ ] simple_term_menu
  - 简洁的终端menu实现
  -  "Windows" is currently not supported.
- [x] rich.logging
  - 华丽的python日志库功能，结合logging库来使用
  - 示例配置：https://calmcode.io/logging/rich.html
- [x] prompt_toolkit
  - 底层的命令支持库，一般不使用，除非用于开发实用库。
- [ ] pick
  - 又一个问答库。
  - 缺点：it uses curses and opens up a new simple GUI, NOT succinct.
- [x] colorama
  - 终端文本添加颜色，简洁轻量。
- [x] click
  - 命令行工具库。强大全面。
- [ ] blessings
  - terminal coloring, styling, and positioning
  - 缺点：not work in windows
- [x] https://github.com/Delgan/loguru
  - 开箱即用，不需要复杂定制的配置即可拥有：时间+level+位置+信息。
  
## issues
1. logger 无法打印多线程中的日志。

## 参考
multiprocess logging

- [在多个线程中记录日志](https://docs.python.org/zh-cn/3/howto/logging-cookbook.html#logging-from-multiple-threads)
- [从多个进程记录至单个文件](https://docs.python.org/zh-cn/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes)
- [(Python 在多进程中使用 logging)](https://zjuturtle.com/2021/11/09/python-multiprocess-logging/)