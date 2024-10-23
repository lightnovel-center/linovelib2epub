## 如何运行这个项目

先决条件：
- 支持 CUDA/CuDNN 的 NVIDIA 显卡，并正确安装对应版本的CUDA Tookit和CuDNN（可选）
- VS Build ToolSet 2022已正确安装，并勾选安装关于VC 14.0+/C++编译的相关依赖。
- 在本地已正确安装conda环境（例如anaconda或者miniconda3）
- 在本地已正确安装了python 3.10版本

步骤：

1. git clone this repo to local
```
git clone https://github.com/Ucas-HaoranWei/GOT-OCR2.0.git
```
2. cd to project home foldler
```
cd git clone https://github.com/Ucas-HaoranWei/GOT-OCR2.0.git
```
3. new a conda env with specific python version and install project dependencies
```
conda create -n got python=3.10 -y
conda activate got
pip install -e .
```
Note:
- 将 pyproject.toml 中的这行 `"deepspeed==0.12.3",` 注释掉，变成 `#"deepspeed==0.12.3",`，本地仅推理不需要这个库。或者你需要使用WSL2环境，这个deepspeed库不支持windows os。
- `pip install -e .` 这一步安装的是Torch的cpu版本，如果你本地具备了NVIDIA CUDA兼容的显卡，建议卸载cpu版本并安装GPU版本。

4. [可选] uninstall torch cpu version and reinstall torch GPU version
```
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
Note:
- 这里 cu124 表示CUDA 12.4.X版本，写此文章时，pytorch官网文档推荐的最新CUDA版本就是 12.4。 [参考](https://pytorch.org/get-started/locally/)。
- 这个 安装的 CUDA 版本取决于你本地 NVIDIA 显卡的CUDA Toolkit驱动版本。可以通过下面的命令示例进行确认。
```
(got) PS D:\Code\OtherGithubProjects\GOT-OCR2.0\GOT-OCR-2.0-master> nvcc -V
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
Built on Thu_Sep_12_02:55:00_Pacific_Daylight_Time_2024
Cuda compilation tools, release 12.6, V12.6.77
Build cuda_12.6.r12.6/compiler.34841621_0
(got) PS D:\Code\OtherGithubProjects\GOT-OCR2.0\GOT-OCR-2.0-master> nvidia-smi
Sat Oct 12 21:03:20 2024
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 560.94                 Driver Version: 560.94         CUDA Version: 12.6     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce MX250         WDDM  |   00000000:01:00.0 Off |                  N/A |
| N/A   60C    P0             N/A / ERR!  |       0MiB /   2048MiB |      1%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```
- pytorch推荐的最新CUDA是12.4,NIVIDA 官网最新CUDA版本是12.6。最佳选择是选择安装CUDA 12.4相关驱动到本地。

5. verify if cuda and cudnn can work with torch

在本地新建一个python文件，写入下面测试代码。
```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.current_device())

from torch.backends import cudnn
print(cudnn.is_available())

x = torch.rand(5, 3)
print(x)
```
正常而言，输出如下:
```
2.4.1+cu124
True
0
True
tensor([[0.4666, 0.7361, 0.9623],
        [0.0503, 0.9484, 0.9212],
        [0.2967, 0.1790, 0.3119],
        [0.5462, 0.7595, 0.5339],
        [0.1213, 0.4013, 0.5636]])

```

6. it's time to install flash-attn
```
pip install ninja
# 下面这行代码是源码编译形式来本地构建flash-attn，一般而言很慢，所以不采用这个方式
#pip install flash-attn --no-build-isolation
```
而是采取使用pre-build的wheel来安装
前往这个[页面](https://github.com/bdashore3/flash-attention/releases)，将合适的whl下载到这个项目文件夹下，然后运行：
```
(got) PS D:\Code\OtherGithubProjects\GOT-OCR2.0\GOT-OCR-2.0-master> pip install flash_attn-2.6.3+cu123torch2.4.0cxx11abiFALSE-cp310-cp310-win_amd64.whl
```

此时项目软件依赖已准备完毕。

7. download weights

原项目的文档在 GOT Weights 章节给出了三个下载方式，这里使用Google Drive方式将其下载，并解压到 GOT-OCR-2.0-master 文件下，参考目录结构如下：
```
(got) PS D:\Code\OtherGithubProjects\GOT-OCR2.0\GOT-OCR-2.0-master\GOT_weights> ls


    目录: D:\Code\OtherGithubProjects\GOT-OCR2.0\GOT-OCR-2.0-master\GOT_weights


Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
------          2024/9/3     14:31            911 config.json
------          2024/9/3     14:31            117 generation_config.json
------          2024/9/3     15:08     1432121416 model.safetensors
------          2024/9/3     14:31        2561218 qwen.tiktoken
------          2024/9/3     14:31            149 special_tokens_map.json
------          2024/9/3     14:31           9470 tokenization_qwen.py
------          2024/9/3     14:31            300 tokenizer_config.json
```

8. it's ready to test demo

```
python GOT/demo/run_ocr_2.0.py  --model-name  ./GOT_weights/  --image-file  /an/image/file.png  --type ocr
```
Note:
- 务必替换 `/an/image/file.png` 为本地存在的截图图片路径。

下面是一个例子：
![screenshot-of-google-drive](./assets/Screenshot-1.png)

```
python GOT/demo/run_ocr_2.0.py  --model-name  ./GOT_weights/  --image-file ..\Screenshot-1.png  --type ocr
```
运行时间取决于显卡算力和flash-attn是否被正确应用，结果如下。
```
<|im_start|>system
You should follow the instructions carefully and explain your answers in detail.<|im_end|><|im_start|>user
<img><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad><imgpad></img>
OCR: <|im_end|><|im_start|>assistant

C:\Users\11372\miniconda3\envs\got\lib\site-packages\transformers\models\qwen2\modeling_qwen2.py:698: UserWarning: 1Torch was not compiled with flash attention. (Triggered internally at C:\actions-runner\_work\pytorch\pytorch\builder\windows\pytorch\aten\src\ATen\native\transformers\cuda\sdp_utils.cpp:555.)
  attn_output = torch.nn.functional.scaled_dot_product_attention(
已使用71%的存储空间一旦存储空间用尽，您将无法创建、修改和上传文件。获取100GB存储空间，
```

Note:
- `UserWarning: 1Torch was not compiled with flash attention` 如果出现这个提示代替flash-attn没有配置正确。可能和CUDA版本一致性或者显卡的架构（必须>=Ampere）有关，具体原因暂时没有进一步探索。这个问题仅影响OCR识别速度，不影响OCR识别结果。

