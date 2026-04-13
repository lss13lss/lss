---
tags: [总结, learning]
title: 个人总结
created: '2025-10-25T07:52:20.502Z'
modified: '2025-12-01T02:25:44.139Z'
---

# 个人总结
用于整理LLM的相关知识
## transformer
从LLM的基础结构入手，分析各个模块用到的方法以及在整个流程中起到的作用，对应有哪些改进的方法。
### 结构以及各部分功能
输入-> 分词器 -> embedding -> encoder -> decoder -> 词表
#### 分词器
输入是自然语言，需要转换成token，这里需要用到分词器(tokenizer),将字符划分成更小的单位。分词器的意义是防止词表过大，以英文单词为例，一共只有26个字母但是组成的单词数量却很多，不同单词之间有共同的词根，比如en，un等等。比如一个hello经过分词器可能变成 he ll o三个token
分词器分为词级分词（未登录词问题），字符级分词（词表小，单个字符语义信息弱），子词级分词（BPE，wordPiece）
- 过程
分词 -> 索引映射 -> 添加标记 -> 填充 -> embedding
*分词器的训练过程*
BPE
在训练过程中首先将语料中的词汇拆分成单个字符，构建初始词表，然后迭代的统计出现频率最高的相邻字符对，合并成新的子词，加入词表，直到词表达到预设大小。
其中在初始化时加入分隔符是为了在划分子词的时候尽可能合法，保留语义信息。
*代码*
```
import torch
 
# 原始句子
raw_text = "我爱学习自然语言处理"
 
# 1. 分词
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
tokens = tokenizer.tokenize(raw_text)
# tokens = ['我', '爱', '学习', '自然', '语言', '处理']
 
# 2. 索引映射
ids = tokenizer.convert_tokens_to_ids(tokens)
# ids = [1416, 4610, 1103, 6210, 7273, 3346]
 
# 3. 添加特殊标记
ids = [101] + ids + [102]  # 加入[CLS]和[SEP]标记
# ids = [101, 1416, 4610, 1103, 6210, 7273, 3346, 102]
 
# 4. padding
max_len = 10
pad_id = tokenizer.pad_token_id  # 0 对应的是[PAD]标记
padded_ids = ids + [pad_id] * (max_len - len(ids))
# padded_ids = [101, 1416, 4610, 1103, 6210, 7273, 3346, 102, 0, 0]
 
# 5. 转为张量
input_ids = torch.tensor([padded_ids])
# input_ids.shape = [1, 10]  形状为[N, T]
 
# 可以重复上述步骤，并在最后一步将多个张量堆叠起来得到批量表示
# batch_input_ids = torch.cat((input_ids, other_input_ids), dim=0)
 
# 最终输入到embedding层
embeddings = embedding_layer(input_ids)
# embeddings.shape = [1, 10, embedding_dim]
```
#### embedding
输入经过分词器后变成one-hot编码，需要和词嵌入矩阵相乘，得到对应的词嵌入向量，最终将输入全部转换成词嵌入向量后可以进行位置编码注入位置信息，再送入后续流程。
emb向量能够表达对象的某些特征，两个向量之间的距离反应了相似性。
向量相似度：点积、余弦相似度
1. word embedding 能够很好的捕捉语义关系
word2vec：CBOW 根据上下文单词预测目标单词 和skip-gram 根据当前单词预测上下文单词
2. sentence embedding
在词嵌入的基础上，将句子映射到向量空间，一般使用预训练的语言模型将句子编码为固定长度的向量，一般将每个token最后一层的输出做均值池化得到一个句向量。
*embedding模型的训练过程*
1. 基于上下文
2. 基于统计信息
3. 基于预训练模型

*代码*

#### 位置编码
自然语言中，相同的字符但是语序不同会呈现出不同的效果，位置编码是为了在进行词嵌入后将位置信息也加入到词嵌入矩阵中，帮助在计算注意力时可以捕捉到位置信息。
点积操作是无序的，我们需要包含位置。
1. 绝对位置编码
直接将绝对位置信息生成一个矩阵加到词嵌入矩阵中，但是这种方法效果一般，实际操作一般用一个可学习矩阵来替代绝对位置编码，但是这种编码方式的拓展性很差
正余弦位置编码，在矩阵变换时会破坏掉相对位置信息。操作是将嵌入向量和位置编码向量直接相加。绝对位置太呆板。
2. 相对位置编码
通过计算当前位置与其他位置的差值来体现位置信息
T5提出了一种较为简化的相对位置编码TS Bias。具体来说，它在注意力分数中引入了可学习的标量，这些标量是基于查询和键的位置之间的距离进行计算的。
T5 不在输入层加任何“位置向量”，而是在每一层 Self-Attention 的 logits 阶段加入一个可学习的相对位置偏置 bᵢⱼ：
Attention(Q,K) = softmax( (QKᵀ)/√dₖ  +  bᵢⱼ  +  mask ) V
bᵢⱼ 只和“位置差” j−i 有关，且被离散化成少量“桶（bucket）”，远距离共用一个桶，精细区分近距位置。
具备一定的外推能力，且应用到transformer的每一层。
3. 旋转位置编码（ROPE）
ds用的方法，通过对词嵌入矩阵进行旋转，实现了绝对位置和相对位置的统一，当两个词嵌入向量点积时就体现了相对位置，根据三角恒等式代换，点积之后的结果除了给定的值之外包含了m-n（相对位置信息）
分别对QK做旋转位置编码，然后计算注意力
把 d 维向量按“相邻两维”切成 d/2 个 2D 平面
给第 i 个平面分配一个固定频率 θᵢ = 10000^(−2i/d)
位置 m 的旋转角度 = m θᵢ
最终旋转矩阵是分块对角矩阵（block-diagonal），无额外参数
4. 其他
最近也出现了很多更优秀的位置编码:
ALiBi 在原始的注意力计算公式上，进一步引入了与相对距离成正比例关系的惩罚因子来调整注意力分数。
DeepSeek提出了解耦RoPE的策略，对Q、K做两部分的拆分，一部分用来表示旋转位置编码（低维度），另外一部分表示文本嵌入（高维度），最后将两部分合并到一块来实现相对位置信息的添加；如下图：前面的高维度向量称为nope，后面的低维度向量称为rope。
YaRN：
非线性差值的方式来外推rope到更长的序列。（长序列压缩成短序列）对于高频使用复杂缩放，对于低频使用普通缩放。

#### encoder
输入进过位置编码后进入encoder，首先经过完整的自注意力计算，归一化后传入FFN，经残差连接后归一化通往下一层。encoder是标准的transformer基本单元但是现在的生成式模型一般不使用encoder，大多是decoder-only的结构。
1. 自注意力
输入经过自注意力后得到QKV矩阵，Q负责查询当前token与其他token的相关程度，K代表当前token的关键信息，V代表当前token起到的重要成都，注意力结果attn = V@softmax（Q@K/(dk**(0.5))
- 这里softmax的作用是将结果进行归一化，抹平信息之间的差距
- 进行缩放的原因是避免点积后过大，这样经过softmax之后会将将较小的结果调的太小

GQA:多Q注意力 节省显存，经工程验证4q共享一个kv是最好的


2. FFN层
这里输出之后的结果经过归一化之后来到FFN，包含两个全连接层和中间的归一化层。这里的权重包含了模型训练过程中学习到的记忆，同时这里归一化作用是？


3. add@norm
残差连接的作用
1. 能够更好的拟合函数，加上一个原始状态能够在拟合上给到好处。通过引入恒等映射（identity mapping），让网络更容易学习，从而提升拟合能力。网络只需要学习“如何修正输入”，而不是“如何完全重构输入”。
2. 能够有效的缓解梯度消失的问题，推导时多了一个+1项，能够很好的解决梯度消失的问题
add代表残差连接，是将输入与FFN得到的结果进行相加，整体上来看提供了一条从输入直接到达输出的通路，这是为了稳定训练，防治出现梯度爆炸或者梯度消失的问题
Norm的作用：
归一化可以确保不同特征或变量之间具有相似的数值范围，有助于提高模型的性能和收敛速度。通过归一化，你可以确保模型不会因为特征值的范围差异而偏向某个特定的特征，而是可以更平衡地利用所有的特征信息来进行预测。防止层内部的计算使得激活值的分布发生剧烈变化；层归一化还可以起到一定的正则化作用，防止模型过拟合；
| # | 位置别称                           | 出现模型                          | 核心作用                                                 | 失效症状（去掉后）                           |
| - | ------------------------------ | ----------------------------- | ---------------------------------------------------- | ----------------------------------- |
| ① | **Pre-LN**（Encoder/Decoder 入口） | T5、GPT-3、LLaMA、ChatGLM        | 让 **每一子层输入** 处于 N(0,1) 邻域，**梯度可回传 100+ 层**；是“深度放大器”  | 训练 >30 层 loss 爆炸，微调学习率必须降 10×       |
| ② | **Post-LN**（原始 Transformer）    | 2017 Transformer              | 保证 **残差支路** 与 **主支路** 尺度一致，**早期 6-12 层最稳**；但加深后梯度衰减大 | 层数 >12 时验证 BLEU 停止提升，加深反而掉点         |
| ③ | **Sandwich-LN**（两头夹）           | 某些 100+ 层 ViT、BERT-large redo | 同时约束 **输入+输出** 方差，**防止“信息膨胀”**，适合极宽 FFN              | 宽 FFN (4×hidden) 出现激活值 1e5 → 梯度 NaN |
| ④ | **RMS-Pre**（均方根归一化）            | LLaMA、Falcon、Mistral          | 去掉均值 μ，仅除 RMS，**减少通信+提升外推**；让 **推理长序列** 分布更稳         | 8 k→32 k 生成时 ppl 暴涨，重复率升高 3×        |

| 作用           | 解释                                                                                                           | 不加的后果                             |
| ------------ | ------------------------------------------------------------------------------------------------------------ | --------------------------------- |
| **① 梯度高速公路** | 把各层输入强行拉回到 N(0,1) 附近，避免 **梯度膨胀/消失**，尤其 100+ 层大模型                                                             | 训练 30 层后 loss 发 NaN，或微调时越学越慢      |
| **② 掩码保护器**  | 自注意力 + causal mask 后，**不同位置的方差差异巨大**（开头 token 只看到 1 个，末尾看到全部）。归一化让“深可见”与“浅可见”处于同一尺度，softmax 不会把早期 token 压成 0 | 生成文本时 **前几个 token 重复/乱码**，长序列尤其明显 |
| **③ 跨模态对齐器** | 交叉注意力前做归一化，**让 Decoder 隐含状态与 Encoder 输出处于同一尺度**，避免“一方太大直接把另一方带跑”                                             | 翻译/摘要任务出现 **漏译、无中生有**             |

- pre-Norm 在token输入的时候进行归一化，这样稳定训练
- Post-Norm 将残差连接后的结果进行归一化，效果好但是容易训练不稳定

SwiGLU​激活函数
核心特性
门控机制：通过Swish激活的权重动态调节信息流，过滤不重要信息；
平滑性：Swish的连续可导性缓解了ReLU的梯度消失问题；
非单调性：允许模型捕捉更复杂的非线性模式；
参数效率：相比传统FFN（ReLU + 线性层），SwiGLU通过门控减少冗余计算。

*代码*
层归一化
Norm = （x - 均值）/（方差 + a）* γ + β
其中可学习参数的作用是把‘强行拉平’的分布重新拉伸/偏移回模型最舒服的那块区域，否则信息会被‘压死’或‘饿
| 参数        | 形状        | 初始化 | 作用                               | 极端案例（去掉后）                                                   |
| --------- | --------- | --- | -------------------------------- | ----------------------------------------------------------- |
| γ (scale) | \[hidden] | 全 1 | **把归一化后的 N(0,1) 重新放大/缩小到最优动态范围** | 全部强制方差=1 → 深层 tanh/sigmoid 输入过小 → **梯度消失**，训练 10 层后 loss 不动 |
| β (bias)  | \[hidden] | 全 0 | **把零均值重新平移，保留非对称激活或残差捷径的直流分量**   | 全部强制均值=0 → 后续 ReLU 一半神经元恒为 0 → **信息坍塌**，BLEU 掉 8 分          |



#### decoder
基本结构和encoder相同，但是注意力为mask attention，因为decoder需要注意当前已知的信息来预测输出
有两个注意力，要接受来自encoder的信息，来计算

```
# ---------------- 训练/推理 demo ----------------
if __name__ == "__main__":
    vocab_size = 10000
    model = TransformerDecoder(vocab_size, d_model=512, n_layers=6, n_heads=8)
    model.cuda()
    opt = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=0.01)

    # 伪数据
    x = torch.randint(0, vocab_size, (4, 128)).cuda()   # [B=4, T=128]
    for step in range(10):
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(
            logits.view(-1, vocab_size), x.view(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()
        print(step, loss.item())
```
#### 结果
经过多层的encoder和decoder后，最后的输出经过一个线性层和softmax层输出，其中线性层负责将输出转换成词表维度，而softmax之后得到最大token的概率。
最后一层隐藏状态 → 线性投影到词表大小 → Softmax 成概率 → 采样/贪心得下一 token（推理）或 整句交叉熵（训练）。
无论 Encoder-Only / Decoder-Only / Encoder-Decoder，最后一步都是同一个 lm_head 矩阵乘法。


#### 各部分计算复杂度分析
从输入输出和结果来分析各部分的计算
### 改进以及效果
#### Encoder-Only
当前的模型主要场景都是生成式，因此encoder结构更适合应对生成式任务
qwen：
输入 Token ID
     ↓ embed_tokens  (vocab×d)
     ↓ + RoPE 旋转位置编码
     ↓  repeated N 次：
     ┌──────────────────────────────────────────┐
     │  Qwen3DecoderLayer（Pre-Norm）            │
     │  ① RMSNorm(输入)                         │
     │  ② GQA 自注意力 + q_norm/k_norm          │
     │  ③ 残差加回                             │
     │  ④ RMSNorm                             │
     │  ⑤ SwiGLU FFN                          │
     │  ⑥ 残差加回                             │
     └──────────────────────────────────────────┘
     ↓  final RMSNorm
     ↓  lm_head (d→vocab)     ← 与嵌入层**不共享**权重
     ↓  Softmax → 概率
     ↓  采样/贪心 → 下一个 Token
#### MOE
混合专家模型，在实际推理的过程中，在全连接层划分不同的专家，每个专家用于应对不同的内容，运算时只激活部分专家进行推理，比如80B-13B表示模型大小为80B但运行时只激活13B的参数，提升效果的同时显著降低了计算资源
通过门控网络来决定是哪一个专家来解决问题，相比于预训练模型，只需要更少的计算资源来进行预训练，相同参数的推理成本更低，拓展能力强，多任务学习能力好
一个典型的门控网络就是一个带有 softmax 函数的简单的网络。这个网络将学习将输入发送给哪个expert，实际操作过程中1.添加噪声（提高模型的鲁棒性和泛化能力，当模型在训练或推理阶段遇到不确定或嘈杂的数据时，鲁棒性较强的模型更能保持稳定的性能。减少过拟合的风险。负载均衡：在MoE模型中，通过加入噪声可以实现不同专家之间的负载均衡。）2.选择保留前K个值3.应用softmax函数，具体操作中一般topk为2-4
- 负载均衡
要理解专家负载均衡，可以从batch size的角度出发。通常来讲，较大的 batch size 推理性能更好，但是由于样本在MoE层激活专家时需要并行，MoE层中每个专家的实际batch size会减少。举个例子，假设当前 batch 有10个token，其中5个token被路由到了某个专家网络，而其他5个token被路由到了其它5个不同的专家网络，这就会导致各专家网络获得的 batch size 不均匀，一个是另外的5倍，就会导致算力利用率不足的问题。
并且，如果我们把所有的token都发送给少数几个头部专家，训练效率将会变得低下。因为在训练中，门控网络会收敛至仅选择少数几个头部专家。这种情况会不断自我强化，因为受青睐的专家训练得更快，它的效果一直在被优化，因此选择它们的频率也会更高。那么此时，这几个少数专家就会过载，每次需要计算大量token，其他的专家模型就得不到训练而被闲置，就会导致模型失衡，性能下降。因此，MoE模型中需要控制专家均衡。上文加入噪声机制，可能就会导致门控在做出选择时跳过几个最优专家模型，去选择其余的专家模型，从而更好地协同工作。

- 公共专家
有部分专家用于处理公共或者一些普通问题
- 美团推出long cat使用零计算专家，既取消了公共专家，进一步降低了推理时的资源占用
*代码*
```
class Expert(nn.Module):
  def  __init__(self, input_size, output_size): 
    super(Expert, self).__init__()
    self.linear = nn.Linear(input_size, output_size)
    
  def forward(self, data):
    x = self.linear(data)
    return x
 
 
class GatingNetwork(nn.Module):
  def __init__(self, input_size, num_experts):
    super(GatingNetwork, self).__init__()
    self.linear1 = nn.Linear(input_size, 4)
    self.relu = nn.ReLU()
    self.linear2 = nn.Linear(4, num_experts)
    self.softmax = nn.Softmax(dim=-1)
  
  def forward(self, data): 
    x = self.linear1(data)
    x = self.relu(x)
    x = self.linear2(x)
    x = self.softmax(x)
    return x
 
 
class MixtureOfExperts(nn.Module):
  def __init__(self, num_experts=2):
    super(MixtureOfExperts, self).__init__()  
    self.expert1 = Expert(2,1)
    self.expert2 = Expert(2,1)
    self.gating =  GatingNetwork(2, num_experts)
    self.sigmoid = nn.Sigmoid()
      
  def forward(self, data):
    expert1_output = self.expert1(data)
    expert2_output = self.expert2(data)  
    
    gating_output =  self.gating(data)
 
    s = (expert1_output*gating_output[:,0][:,None] + 
         expert2_output*gating_output[:,1][:,None])
    
    a = self.sigmoid(s)
    
    return a
 
  def backward(self, y_hat, labels, criterion, optimizer): 
    optimizer.zero_grad()
    loss = criterion(y_hat, labels)    
    loss.backward()
    optimizer.step()
    return loss.item()
 
 
# Define the model, loss, and optimizer
moe = MixtureOfExperts()
criterion = nn.MSELoss() 
optimizer = torch.optim.Adam(moe.parameters(),lr=0.01)
 
# Define the learning rate scheduler
scheduler = torch.optim.lr_scheduler.ConstantLR(optimizer) 
 
# Convert data and labels to float tensors
data_tensor = data.float()
labels_tensor = labels.view(-1, 1).float()
 
# Training loop
num_epochs = 500 
for epoch in tqdm(range(num_epochs)):
    # Forward pass
    y_hat = moe.forward(data)
 
    # Backward pass and optimization
    loss_value = moe.backward(y_hat, labels_tensor, criterion, optimizer)
 
    # Decay the learning rate
    scheduler.step()
 
 
expert1_weights = moe.expert1.linear.weight.detach()[0,0]
expert2_weights = moe.expert2.linear.weight.detach()[0,0]
 
expert1_bias = moe.expert1.linear.bias.detach()
expert2_bias = moe.expert2.linear.bias.detach()
 
gating_weights = moe.gating.linear2.weight.detach().flatten()
 
x_line = np.linspace(min(data[:, 0]), max(data[:, 0]), 100)
 
y_line1 = expert1_weights * x_line + 5
y_line2 = expert2_weights * x_line + 5
 
class_0 = data[labels == 0]
class_1 = data[labels == 1]
plt.scatter(class_0[:, 0], class_0[:, 1], label='Class 0', alpha=0.5)
plt.scatter(class_1[:, 0], class_1[:, 1], label='Class 1', alpha=0.5)
 
plt.plot(x_line, y_line1, label='Expert 1', alpha = 1)
plt.plot(x_line, y_line2, label='Expert 2', alpha = 1)
 
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.grid(True, c='gray')
plt.legend()
plt.autoscale()
plt.show()
```

#### 注意力
1. MHA
多头注意力，每个头用于捕捉不同维度的信息，相当于从多个维度进行信息提取，每个维度可以从不同的维度来分配注意力


2. MQA
多Q注意力，为了降低显存占用，使用公共的KV矩阵而生成不同的Q，相当于每个Q来查询不同维度的信息
3. GQA
组Q注意力，结合了MHA和MQA，分成多个组，在每个组中多个Q共享KV矩阵，做一个折中

4. MLA
多头潜在注意力，为了进一步降低KV，在做KVcache的时候对KV做降维操作，在实际计算的时候再将维度重新还原，相当于时间换空间。
```
class MLA(nn.Module):
    def __init__(self, d_model, n_heads, latent_dim, dropout=0.1):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.latent_dim = latent_dim               # 通常 d/4
        self.scale = self.head_dim ** -0.5

        # 压缩
        self.kv_compress = nn.Linear(d_model, 2 * latent_dim, bias=False)
        # 解压
        self.kv_decompress = nn.Linear(latent_dim, n_heads * self.head_dim, bias=False)
        self.v_decompress = nn.Linear(latent_dim, n_heads * self.head_dim, bias=False)

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)
        self.drop = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        B, T, C = x.shape
        # 1. 压缩 KV
        kv_latent = self.kv_compress(x)                      # [B, T, 2*latent]
        k_lat, v_lat = kv_latent.chunk(2, dim=-1)            # [B, T, latent]

        # 2. 解压到多头空间
        k = self.kv_decompress(k_lat).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_decompress(v_lat).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        # 3. Q 正常多头
        q = self.q_proj(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

        att = (q @ k.transpose(-2, -1)) * self.scale
        if mask is not None:
            att += mask
        att = att.softmax(dim=-1)
        att = self.drop(att)

        out = att @ v
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.o_proj(out)
```
5. flash attention


## train
通过对模型进行训练，使得模型具备通用或者具体的功能，同时整理训练过程中的参数
关键点
- 数据
- 参数
- 损失函数：衡量模型答案与真实答案的差距
- 优化器：调整参数的学习方法，如梯度下降
- 正则化：防止AI死记硬背的记忆抑制器
### 预训练
需要大量的数据做无监督学习，用于训练基座模型，语言模型
1. 数据流设计:动态分块、掩码生成
2. 初始化：模型参数初始化，优化器初始化
3. 前向传播：并行化策略（并行，ZERO），激活重计算
4. 损失计算：交叉熵/MSE,正则化、权重衰减
5. 反向传播：梯度计算、梯度累积
6. 参数更新：优化器步骤、学习率调整

正则化：
防止更新过大导致过拟合，在损失函数中加入惩罚项   加入一个控制正则化力度的超参数
L1这正则化：损失函数加上权重绝对值；L2正则化：损失函数加上权重绝对值的平方

Doupout：
随机丢弃部分参数，防止过分依赖某些关键参数

*代码*
损失函数
均方误差MSE
```
import torch
import torch.nn as nn

# 假设 pred 和 target 都是形状 [N, *] 的张量
pred   = torch.randn(32, 1, requires_grad=True)
target = torch.randn(32, 1)

mse = nn.MSELoss()          # 直接调用官方实现
loss = mse(pred, target)    # 标量
print(loss.item())

# 若只想看公式，不依赖 nn.MSELoss：
loss_manual = ((pred - target) ** 2).mean()
print(loss_manual.item())
```
交叉熵
```
import numpy as np

def softmax(x):
    # x: [N, C]
    x_max = x.max(axis=1, keepdims=True)
    exp = np.exp(x - x_max)          # 防溢出
    return exp / exp.sum(axis=1, keepdims=True)

def cross_entropy_np(logits, y_true):
    """
    logits: [N, C]  未归一化
    y_true: [N]     0~C-1 的整数
    """
    probs = softmax(logits)
    N = logits.shape[0]
    log_probs = -np.log(probs[range(N), y_true] + 1e-12)  # 防 log(0)
    return np.mean(log_probs)

# 示例
logits_np = np.random.randn(5, 4)
labels_np = np.array([0, 3, 1, 2, 1])
print(cross_entropy_np(logits_np, labels_np))
```
### SFT
微调，构建特定的数据集来微调模型，相当于将制定的知识通过微调注入模型，适用于高难度的任务，典型场景比如蒸馏，但是微调可能会损害模型的泛化性。另外微调的模型是不可能超过蒸馏的原始模型的能力的

数据格式
1. 数据差异：
| 维度 | 预训练 | 微调 |
|---|---|---|
| 样本来源 | 无标注纯文本，连续 512-4096 token 滑动窗口 | 下游任务已标注样本（分类标签、QA 对、摘要-原文对） |
| 一条样本长度 | 单文档截断，pad 到固定长度 | 任务决定：句子对拼起来常＜256 token，pad 极少 |
| 掩码策略 | 随机 15 % mask 或 causal mask | 不再随机 mask，只在“标签位置”计算 loss（如 [CLS]、answer span、生成第一个 token 到最后一个 token） |
| batch 构成 | 同一语料 shuffle 后连续取 | 按任务标签 stratified sampling，保证每卡各类别比例均衡 |
2. 前向传播差异
微调：
– 分类／回归：只取 [CLS] 或 eos 位置的最后一层 hidden h，过一层新“任务头” W_task（随机初始化）得到 logits。
– 生成式：用 decoder 自回归一次性产出答案，loss 只累计“答案部分”的交叉熵，问题部分被 ignore_index 掩掉。
因此 99 % 的骨干参数虽然参与前向，但它们的激活梯度在“非标签位置”被置零。

3. 任务头最先拿到梯度 ∇W_task，幅度最大（因为是随机初值）。
4. 梯度继续往深层传，但：
– 低 LR + 零 decay 使每一步更新量≈预训练的 1/10～1/100。
– 早期停止通常在 2-10 epoch 内完成，等效于参数沿“预训练盆地”做微小随机游走，而不是跨盆地跳跃。
5. 经验观察：顶层 2-4 层梯度范数占总梯度能量 70 % 以上，底层几乎不动；这与预训练“梯度随深度均匀下降”形成鲜明对比。
#### 全量微调
修改全部参数
#### lora
使用低秩矩阵，冻结模型的原始权重，通过更新低秩矩阵来微调模型，显著减少了显存占用，可以达到全量微调一样的效果。迭代次数一样吗？
#### 训练框架
Llama Factory
#### 训练参数
1. 学习率
2. batchsize
3. chackpoint
4. warmup

### RL
强化学习，对模型进行规训，适用于中低难度的任务
通过强化学习可以将语言模型转换为对话模型
- 强化学习比sft更可以考虑整体的影响，sft针对单个token进行反馈，目标是要求模型针对给定的输入给出的确切答案，而rl是针对整个输出的文本进行反馈，不针对特定的token，反馈的粒度不同，可以兼顾表达的多样性，可以增强对微小变化的敏感性。
- 强化学习更容易解决幻觉问题，主要有三类输入 文本型、求知性、创造性。   sft非常容易使得求知型query产生幻觉。rl可以通过定制奖励函数，将答案进行区分，使得模型可以学会依赖内部知识放弃回答，一定程度上缓解幻觉问题
- 强化学习可以更好的解决多轮对话奖励积累的问题：多轮对话是否

强化学习的目标函数包含两部分，一部分是希望结果与之前sft的回答分布近似，  二是模型的回答都是高分回答

#### PPO
近端策略优化，有四个模型，polity， reference， reward， critic，其中policy用于产生策略，reference用于计算更新的程度，reward用于衡量奖励，critic用于衡量优势，其中policy和critic需要更新
目标函数包括似然函数，梯度裁剪
奖励包含KL散度
#### DPO
直接偏好优化
使用有偏好的数据来训练，本质上不算是RL算法，训练过程简单，通过数学推导将优势用policy来表示
#### GRPO
PPO的优化方法，取消了critic，少了一个需要更新的模型，显著降低了显存占用。集体的方法是使用组内相对优势来取代优势，同一个prompt一次产生多个结果为一组，这些多个结果的平均奖励为基线，通过与平均奖励的差值来体现优势。将KL散度从奖励提到目标函数中，更改了KL的表达式
#### DAPO
在GRPO的基础上做改进，主要有动态采样，裁剪区间解耦，token级的优势估计等等
#### 其他

## 推理及部署
### 显存占用分析
### 部署方法

## RAG
在智能客服场景下的重要组成部分，针对不同的场景有多种技术可以选择。
核心思想是通过外部构建知识库来给模型提供专业的参考知识来辅助生成答案。
原因： 1.时效性，大模型语料不能及时更新 2. 安全性，有些数据是隐私的，不能拿来训练  3.精确性，有时需要模型严格按照说明文档来回答，避免幻觉。

### 整体流程
query -> doc collection index -> search -> reference doc -> LLM

1. query 理解： 需求识别，query改写、补充，核心词提取，纠错、
2. 原始文档： 内容理解，文档解析，多模态内容理解，数据增强（生成摘要）
3. 内容分片。构建索引：常见向量索引，倒排索引，吐数据库
4. 召回： 向量检索，关键词检索，图谱检索，agent流


### query理解
用户的问题不一定适合直接拿来检索，效果一般，不同的query有不同的后续处理动作，需要对query需求分类。
根据业务需求来，常见包括一如分类，比如做时效性分类，或者映射到一个意图列表等。改写就是多轮对话的省略补全，或者提取出核心的搜索词，同义词的扩写和纠错。
搜索时效性模型：对耗时要求高，耗时100ms左右
多轮改写模型，需要比较强的寓意理解和推理能力，500ms左右
### 内容理解
1. 文档解析，原始文档提取重要信息，去除噪音。图片表格进一步理解，生成可以用来检索的文本。
2. 信息增强，针对 文档片段，生成可能的问题，摘要，构件图（提取实体，关系等）
3. 构建索引，找回文本和检索文本。建倒排索引的话，检索文本是比较短的，一般是多粒度的切词的文本。很多情况下检索文本和召回文本是不一样的
4. 文本切分 基于规则：特定符号，递归切分   基于模型：保证切分后的语义完整性，独立性。

### 分块和向量化
分块：文本切分，考虑块的大小，考虑embedding模型的的处理能力。使用文本分割器，元数据等等
向量化： 使用模型。并非简单的取最后一个token向量，通过模型的嵌入模型和池化策略，讲一段文本的语义信息压缩成一个固定长度的高维向量。
- 选取最后一个有效token的隐藏状态作为整个文本块的向量表示。因为最后一个token能捕捉到之前的完整上下文信息。
- cls池化：在输入开头插入一个cls标记，训练让这个标记的隐藏状态包含整个序列的摘要信息。
### 检索方法
1. 倒排索引：对文档内容做切词，生成倒排索引，搜索时候根据倒排索引知道在哪个文档中出现过，就去召回这个文档的内容
rag中的经典用法：知识库切成chunk-> 建立倒排 -> 用户query来了先分词 -> BM25打分 -> 取topN 喂给llm
稀疏+向量：一路走倒排拿，一路走向量索引拿
2. 向量检索：向量和文本都转化为float数组，做召回时计算向量相似度，召回最相似的文档

### 召回重排
主流使用bert架构，百兆级别用的最多。
排序模型可以拿到候选文本去算cross attention，排序模型的效果会好一些
召回模型只是看一眼，query和doc被打成向量，点积完事，doc侧的信息在内存里是被冻结的的，看不到query的上下文。重排阶段数据量变少，计算量不再是瓶颈，模型可以吧query和doc完整喂给transformer，让query的每个token去和doc的每个token计算交叉注意力，相当于开卷考试，能解决同义词，句法变换，实体对其，长距离依赖等问题。 
召回负责快刀斩乱麻，重排负责拿放大镜逐字逐句对答案。

### 过滤
可以基于关键词，元数据等进行过滤

### 搜索索引
传统flat：暴力法计算查询向量与所有向量块之间的距离
高效：HNSW，聚类，树状

- 层次索引 如果从大量文档中检索，可以创建两个索引，一个由摘要组成，一个由文档快组成，分两步进行搜索，先通过摘要过滤出相关文档，再在相关文档中进行搜索。
- Hyde 每个块生成假设性问题进行嵌入
- 上下文增强：父文档检索器
- 融合检索或者混合检索 一个基于传统方法，一个基于语义检索



## 记忆
几种方式的弊端和考虑
### mem0
持久化记忆解决方案
双阶段记忆处理流程-提取和更新
#### 提取阶段 
系统会同时从三个来源接受上下文：新一轮的交互，动态滚动的摘要，最近的m条信息
记忆生成：利用LLM来提炼出一组间接的候选记忆
异步刷新：后台模块会异步的，不间断的刷新长期摘要，确保核心推理过程不会因为记忆管理而停顿


#### 更新阶段
相似度对比：生成的候选记忆会与向量库中的top-k个相抵的已有记忆进行比较
智能决策：
添加：存入一条新的记忆；    更新：迭代或者合并一条现有记忆    删除：移除相矛盾或者过时的旧记忆    无操作：无需更改

## agent
新兴概念，目前很多公司在做，是比较有前景的AI落地场景
### 框架
### 组件
### MCP

## A2A
多agent之间沟通的框架
