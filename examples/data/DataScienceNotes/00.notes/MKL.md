---
tags:
  - accelerate
  - CXX
date: 02.10.25
layer: bronze
---
MKL a.k.a. Math Kernel Library от Intel - набор оптимизированных решений для линейной алгебры и проч. мат пейлоадов на основе DPCXX.

В контексте моей работы ДС встречается в качестве *drop-in-place* замены для OpenBLAS и проч. для ускорения научных библиотек питона, в т.ч. numpy & scipy.

```bash
pip install mkl mkl-devel mkl-service
```