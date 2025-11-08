---
tags:
  - py
  - accelerate
date: 02.10.25
layer: bronze
---
При сборке новых версий scipy с [[Common numerical py libs with MKL|кастомным blas-бэкэндом]] изменения site.cfg недостаточно: начиная с 1.9 scipy использует [[meson]] в тулчейне, *который без дополнительных аргументов потребует в любом случае наличия OpenBLAS*.

Для обхода требуется указать дополнительные аргументы уже meson'а через -D, итоговый вариант:
```bash
pip install -U --force --config-setting=setup-args="-Dblas=mkl" --config-setting=setup-args="-Dlapack=mkl" .
```

Т.е. надо явным образом прокинуть аргумент-название лапака и бласа в мезон при сетапе, для этого нужно, чтобы [[pkg-config]] точно имел mkl.pc файл, который может отсутствовать или быть поврежден при установке mkl через conda или pip

``` pkg-config
prefix=/opt/conda/lib
exec_prefix=${prefix}
libdir=${exec_prefix}/libs
includedir=${prefix}/include

Name: MKL
Version: 2023.1.0
Libs: -L${libdir} -mkl_rt
Cflags: -I${includedir}
```

$\Uparrow$ пример  для [[conda]] установки в /opt  mkl\==2023.1.0