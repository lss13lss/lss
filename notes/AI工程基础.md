---
tags: [learning]
title: AI工程基础
created: '2025-08-22T07:06:20.163Z'
modified: '2025-08-25T01:32:47.998Z'
---

# AI工程基础
## 多层感知机
### 线性模型
### 激活函数
线性变换中引入非线性，可以让多层网络更有价值，增强表达能力，处理更复杂的问题。
- sigmoid fx=1/exp(-x) 导数 fx’=fx（1-fx）
- relu fx=max(0,x) fx‘=(1，x>0,0 x <=0)
### 多层感知机
#### 单层MLP
输入*权重->非线性激活->得到loss
训练过程就是不断优化损失函数
#### 多层感知机
## 训练和推理
### 推理
### 训练
#### 更新参数权重
通过梯度寻找函数最小值。
- 反向转播：通过调整权重将输出与目标的差距尽可能缩小，实际做法通过损失函数的最小值来找到对应的权重参数
- 损失函数：用来描述模型的输出和真是情况的差异，一般用MSE（均方误差）其他可能有交叉熵，余弦相似度等
- 学习率 每次更新的步长，学习率是超参数，权重是普通参数
- 链式法则，复合函数求导用
### transfomer
大模型的基石，处理序列数据时，每个元素都可以与序列中的其他元素建立关联，而不仅仅依赖相邻位置的元素
基于qkv操作阶段和v阶段，qk寻找不同位置之间内容的相关度，v按照前序权重对v进行加权求和。
#### 工作原理
核心为编解码器，两个组件的核心都是多头注意力模块。不同注意力模块来优化词的不同含义。解决多义性问题。
解码器有区别，解码器已经预测到的Q去查询编码器中信息的相关度（编码器的KV）
https://blog.csdn.net/Small___ming/article/details/123519699?utm_medium=distribute.pc_relevant.none-task-blog-2~default~baidujs_baidulandingword~default-1-123519699-blog-128317763.235%5Ev38%5Epc_relevant_sort&spm=1001.2101.3001.4242.2&utm_relevant_index=4
https://mp.weixin.qq.com/s?__biz=MzU0MDQ1NjAzNg==&mid=2247536362&idx=2&sn=a3504371106087c5bc38620a11c25ec9&chksm=fb3aebe1cc4d62f7f0f473fff861498f3e16b5a190aa6b8cd339b11b74bbc5e86642cae45392&scene=27
## 优化手段
### 并行
#### 数据并行
每个CPU都维护完整的副本，输入数据拆分到不同部分。
#### 张量并行
模型参数拆分到不容GPU上
##### 多层感知机切
##### attention切
#### 流水线并行
### 分布式训练框架
pytorchDP
pytorchDDP
FSDP
### 推理优化常用手段
#### KV cache
前序上下文的重复计算，将这部分结果值缓存，减少计算量来优化效率
#### 量化
参数，kvcache，激活，通信以及qkv均可以量化
#### prrfill，decode分离
他俩分别是计算密集型和现存密集型，分离部署提升效率
### 占用显存计算
- 训练：参数+梯度+优化器+激活值
参数：参数量*精度占用字节，7B，fp32；参数占28B
优化器：adam是两倍参数量，每个参数维护一个一阶距和二阶矩；SGD没有额外显存占用，
梯度：与参数量相同
激活值：激活数量*batch大小*精度大小--调整batchsize，或混合精度训练。
计算公式batchsize*sequencelen*hiddensize*numlayer*numattentionhead
推理：kv catch + 参数 + 激活值

