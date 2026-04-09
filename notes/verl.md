---
tags: [learning]
title: verl
created: '2025-09-04T08:15:33.478Z'
modified: '2025-09-04T08:18:07.437Z'
---

# verl

```
# Step1: 根目录下创建环境配置
mkdir training_env
cd training_env

# Step2: 挂代理，装依赖
export http_proxy=http://9.21.0.122:11113
export https_proxy=http://9.21.0.122:11113

# Step3: 安装UV包管理
pip install uv

# Step4: 安装CUDA12.4 && 同时应用环境变量
wget https://raw.githubusercontent.com/bitsandbytes-foundation/bitsandbytes/refs/heads/main/install_cuda.sh
bash install_cuda.sh 124 ~/local 1
source ~/.bashrc

# Step5: 虚拟环境创建（Conda是啥真不熟）
uv venv --python 3.10 --seed
source .venv/bin/activate

# Step6: 安装CUDNN
pip install nvidia-cudnn-cu12==9.8.0.87

# Step7: 安装Verl依赖
git clone https://github.com/volcengine/verl.git
cd verl
bash scripts/install_vllm_sglang_mcore.sh

# Step8: 安装Verl
pip install --no-deps -e .
```

环境能力测试
请参考左侧「verl训练」中第0节内容，这里务必跑通PPO和GRPO的测试代码。
（目前单机多卡内容Ready，待测试多级多卡）

4. 方便taiji代码读写—安装Codeserver（可选，此步骤可以不操作）
项目地址：https://github.com/coder/code-server

安装脚本（需要挂代理）：

curl -fsSL https://code-server.dev/install.sh | sh
修改配置文件

vim /root/.config/code-server/config.yaml

image.2.png
保存运行

code-server

PPO测试
```
# Step1: 数据集准备
python3 examples/data_preprocess/gsm8k.py --local_dir ~/data/gsm8k

# Step2: 模型下载
python3 -c "import transformers; transformers.pipeline('text-generation', model='Qwen/Qwen2.5-0.5B-Instruct')"

# Step3: 执行PPO训练（基于Qwen2.5-0.5B-Instruct）
PYTHONUNBUFFERED=1 python3 -m verl.trainer.main_ppo \ 
 data.train_files=$HOME/data/gsm8k/train.parquet \ 
 data.val_files=$HOME/data/gsm8k/test.parquet \ 
 data.train_batch_size=256 \ 
 data.max_prompt_length=512 \ 
 data.max_response_length=256 \ 
 actor_rollout_ref.model.path=Qwen/Qwen2.5-0.5B-Instruct \ 
 actor_rollout_ref.actor.optim.lr=1e-6 \ 
 actor_rollout_ref.actor.ppo_mini_batch_size=64 \ 
 actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4 \ 
 actor_rollout_ref.rollout.name=vllm \ 
 actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=8 \ 
 actor_rollout_ref.rollout.tensor_model_parallel_size=1 \ 
 actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \ 
 actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=4 \ 
 critic.optim.lr=1e-5 \ 
 critic.model.path=Qwen/Qwen2.5-0.5B-Instruct \ 
 critic.ppo_micro_batch_size_per_gpu=4 \ 
 algorithm.kl_ctrl.kl_coef=0.001 \ 
 trainer.logger=console \ 
 trainer.val_before_train=False \ 
 trainer.n_gpus_per_node=1 \ 
 trainer.nnodes=1 \ 
 trainer.save_freq=10 \ 
 trainer.test_freq=10 \ 
 trainer.total_epochs=15 2>&1 | tee verl_demo.log

```
GRPO
```
set -x
ENGINE=${1:-vllm}

HYDRA_FULL_ERROR=1 python3 -m verl.trainer.main_ppo \ 
    algorithm.adv_estimator=grpo \ 
    data.train_files=/root/zexin_cq10_disk/agent-rl/data/geo3k/train.parquet \ 
    data.val_files=/root/zexin_cq10_disk/agent-rl/data/geo3k/test.parquet \ 
    data.train_batch_size=32 \ 
    data.max_prompt_length=1024 \ 
    data.max_response_length=2048 \ 
    data.filter_overlong_prompts=True \ 
    data.truncation='error' \ 
    data.image_key=images \ 
    actor_rollout_ref.model.path=/root/zexin_cq10_disk/agent-rl/model/Qwen2.5-VL-7B-Instruct \ 
    actor_rollout_ref.actor.optim.lr=1e-6 \ 
    actor_rollout_ref.model.use_remove_padding=True \ 
    actor_rollout_ref.actor.ppo_mini_batch_size=8 \ 
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2 \ 
    actor_rollout_ref.actor.use_kl_loss=True \ 
    actor_rollout_ref.actor.kl_loss_coef=0.01 \ 
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \ 
    actor_rollout_ref.actor.entropy_coeff=0 \ 
    actor_rollout_ref.model.enable_gradient_checkpointing=True \ 
    actor_rollout_ref.actor.fsdp_config.param_offload=False \ 
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \ 
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=2 \ 
    actor_rollout_ref.rollout.tensor_model_parallel_size=2 \ 
    actor_rollout_ref.rollout.name=$ENGINE \ 
    actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \ 
    actor_rollout_ref.rollout.enable_chunked_prefill=False \ 
    actor_rollout_ref.rollout.enforce_eager=False \ 
    actor_rollout_ref.rollout.free_cache_engine=False \ 
    actor_rollout_ref.rollout.n=3 \ 
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=2 \ 
    actor_rollout_ref.ref.fsdp_config.param_offload=True \ 
    algorithm.use_kl_in_reward=False \ 
    trainer.critic_warmup=0 \ 
    trainer.logger=['console'] \ 
    trainer.project_name='verl_grpo_example_geo3k' \ 
    trainer.experiment_name='qwen2_5_vl_7b_function_rm' \ 
    trainer.n_gpus_per_node=4 \ 
    trainer.nnodes=1 \ 
    trainer.save_freq=20 \ 
    trainer.test_freq=5 \ 
    trainer.total_epochs=15 $@
```
