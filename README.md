# mcsAna
Minecraft服务器参与建筑玩家统计脚本

基于服务器日志按日分析

当前支持统计玩家在线时长、使用了命令的次数（如玩家使用[WorldEdit](https://modrinth.com/plugin/worldedit)就会在后台留下命令使用的日志）

一切统计基于玩家正常的建筑行为，挂机、刷指令等行为需自行筛选剔除

# Windows使用
- 将服务器日志放在任一空文件夹内
  - 如果日志是以.log.gz压缩包文件组成，请全选后右键全部解压缩
  - 解压缩后，删除.gz压缩包，如果有latest.log文件，请和其他.log文件一样以**日期-序号.log**规则命名
    - 如果latest.log是2025年3月29日的日志，且刚刚已经解压出来了一个2025-03-29-1.log，那么把他改成2025-03-29-2.log即可
- 整理完日志的文件夹应该看起来长这样

![整理完日志的文件夹](https://img.alicdn.com/imgextra/i4/2200604020099/O1CN01O28HzL1CbOGGHNHO5_!!2200604020099.png)

- 在[Releases](https://github.com/GoldenEggsUNION/mcsAna/releases)下载mcsAna.exe主程序
- 直接拖入到刚刚存放log的目录中双击，就是这么简单

![执行效果](https://img.alicdn.com/imgextra/i3/2200604020099/O1CN01kzEqm01CbOGGP4PP4_!!2200604020099.gif)
- 在新生成的view文件夹中，你可以找到每天的日志分析数据，供你参考分析

![数据效果](https://img.alicdn.com/imgextra/i3/2200604020099/O1CN01I3oQEW1CbOGGv67yM_!!2200604020099.png)

**只统计君子，不统计小人**

# 贡献
笔者只是造了一个轮子，更多内容欢迎贡献

（比如 接入[CoreProtect](https://modrinth.com/plugin/coreprotect)）
