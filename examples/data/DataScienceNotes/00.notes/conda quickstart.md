---
tags:
  - DevOPS
date 🗓️: 2025-10-21
time ⌚: 03:10:04
layer: bronze
---
Miniconda - стандартный компактный дистрибутив, достаточен для обеспечения работы простого python-workspace'а в частности. Однострочный `ctrl+C`/`ctrl+V` установки:  
```bash
wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh - O ./miniconda.sh && \
/bin/bash ./minicinda.sh -b -p /opt/conda && \
rm ./miniconda.sh
```
Для активации и работы с cond'ой потребуются махинации с терминалами, однако шорткат в виде шел-хука позволяет сразу после установки активировать окружение и создать новое:
```bash
eval "&(conda shell.bash hook)" && \
conda create -n <ENV_NAME> --clone base -y && \
conda activate <ENV_NAME>
```
___
В случае развертывания воркспейса на [[Docker]], например, картина выглядит еще логичнее, так как в базовом образе удобно можно совершить надстройки в `base` cond'ы каких-то корневых пакетов (как в кейсе [[Задача с образом]]) и затем клонить их в ситуативные окружения под отдельные задачи:
```Dockerfile
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh - O ./miniconda.sh && \
	/bin/bash ./minicinda.sh -b -p /opt/conda && \
	rm ./miniconda.sh
```
...
![[MKL]]
...
```Dockerfile
RUN eval "&(conda shell.bash hook)" && \
	conda create -n mkl_accelerated_env --clone base -y && \
	conda activate mkl_accelerated_env
```