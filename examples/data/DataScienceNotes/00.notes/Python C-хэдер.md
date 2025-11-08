---
tags:
  - CXX
  - py
date: 07.10.25
layer: bronze
---
По аналогии с [[Common numerical py libs with MKL#Примечание о devel|MKL]] питон может быть поставлен в  дефолтной комплектации без сишных хэдеров Python.h, что будет видно при сборке некоторых пакетов (напр. [[python-meson сборка scipy с MKL]]). На уровне *apt* требуется выбрать dev-дистрибутив.
```bash
sudo apt install pythonX.YY
```
$$\Downarrow$$
```bash
sudo apt install pythonX.YY-dev
```

В conda по дефолту поставляется версия с хэдерами
```bash
conda install python=X.YY
```
___

В случае фактического наличия хэдеров (т.е. нормально прошедшей установки в конде) может возникнуть ошибка при билдах **file not found Python.h**, вариант разрешения - явное указание в переменных окружения: 
```bash
export C_INCLUDE_PATH=/opt/conda/include/pythonX.YY:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=/opt/conda/include/pythonX.YY:$CPLUS_INCLUDE_PATH
```