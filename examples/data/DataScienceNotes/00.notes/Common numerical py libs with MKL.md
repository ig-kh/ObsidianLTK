---
tags:
  - accelerate
  - py
date: 02.10.25
layer: bronze
---
Для ускоренной работы numpy+scipy сборка может быть осуществлена сборка с [[MKL]].

Для старых версий (numpy<2.0 & scipy<=1.8) настройка пайплайн достаточно прост - после установки intel mkl & mkl-devel в конфигах либ перед билдом нужно указать хэдеры:
```site.cfg
[mkl]
include_dirs = /opt/conda/include
library_dirs = /opt/conda/lib
mkl_libs = mkl_rt                  # mkl_libs = mkl
lapack_libs =                      # lapack_libs = mkl_lapack

```
$\Uparrow$ пример  для [[conda]] установки в /opt

Далее стандартным образом через pip install . устанавливаются посредством setup tools с переменными сборки numpy:

```bash
export NPY_BLAS_ORDER = MKL
export NPY_LAPACK_ORDER = MKL
```
___
### Примечание о devel
По аналогии со многими пакетами MKL-devel - это версия MKL development, содержащая плюсовые/сишные хэдэры, необходимые для сборок на ее основе.