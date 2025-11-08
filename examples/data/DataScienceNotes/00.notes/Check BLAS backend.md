---
tags:
  - accelerate
  - py
layer: bronze
---
```python
import numpy as np
import scipy as sp

print(np.show_config())
print(sp.show_config())
```

Просмотр конфигов укажет на бэкенды сборки даже без mkl-service для рантайма.

Результаты для успешной [[Common numerical py libs with MKL|ускоренной сборки]] должны будут содержать явные указания на MKL: `blas_mkl_info` & `lapack_mkl_info` подпункты.

Для numpy:
```config
...
blas_mkl_info:
	libraries = ['mkl', 'pthread']
	library_dirs = ['<ENV_PATH>/lib']
	define_macros = [('SCIPY_MKL_H', None), ('HAVE_CBLAS', None)]
	include_dirs = ['<ENV_PATH>/include']
...
```