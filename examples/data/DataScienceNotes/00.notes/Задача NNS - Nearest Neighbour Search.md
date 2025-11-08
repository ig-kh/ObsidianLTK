---
tags:
  - MathModeling
  - Search
date: 2025-10-27
time: 21:48:27
location:
layer: bronze
---
### Постановка задачи NNS
Задача поиска ближайших соседей формализуется в простом случае следующим образом:
Есть множество объектов $X, x\in X, |X|=N$, являющихся многомерными векторами фиксированной размерности $d\in \mathbb{N}: x\in\mathbb{R}^d$; есть запрос $q\in\mathbb{R}^d$ и для него требуется найти $k\in\mathbb{N}\leq N$ ближайших объектов из $X$
$$\{x_0^\star\, ... x_{k-1}^\star\} = argmin_{x\in X}^k|q-x|$$
### Постановка апроксимации
В задаче возможно контролировать trade-off скорости и точности аппроксимацией - *ANN* : Approximate Nearest Neighbours. 
$$\{x_0^\star\, ... x_{k-1}^\star\} = _\epsilon\widetilde{argmin}_{x\in X}^k|q-x|$$
### Приложения
- Рекомендательные системы (равно и как любой другой Embedding-Tying в нейросетях)
- Поиск похожих изображений/текстов
- Кластеризация, классификация (kNN)
- Информационный поиск
___
***Задача поиска ближайших имеет серьезную уязвимость к проклятию размерностей, если решать ее [[|классическими методами]]***

Brute-force - $O(nd)$, KD-tree - построение $O(n\log n)$ и средний поиск $k: O(\log n +k)$, но сильная деградация качества при росте $d$ наблюдается в worst-case поиска - $O(n^{1-1/d})$ при $d\rightarrow \infty$ очевидно сойдется к линейному $O(n)$ [https://proceedings.neurips.cc/paper_files/paper/2007/file/9fc3d7152ba9336a670e36d0ed79bc43-Paper.pdf]
___
*Source:* [[Navigable-Small-Worlds_Graph-Based-NN-Search]]