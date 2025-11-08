---
tags:
  - ML
  - STATS
date: 2025-11-07
time: 21:04:53
location:
layer: bronze
---
*BVD* - концепт, выражаемый в функциональных зависимостях и строго доказуемый для некоторых функционалов ошибки.
Bias Variance (Noise) Decomposition - разложение общей ошибки $R(a)$ семейства моделей $\mathcal{A}$ на данных $\mathbb{X},\mathbb{Y}$  
$$R(a) = \int_{x\in\mathbb{X}}\int_{y\in\mathbb{Y}}\bigg[\mathbb{p}(x,y)*\mathcal{L}(y, a(x))\bigg]$$
$\uparrow$ для конкретной модели в интегральном виде ошибка есть такова, что равно $R(a) = \mathbb{E}_{x,y}\mathcal{L}(y,a(x))$ 
$$\mathcal{L}(\mu) = \mathbb{E}_{x,y}\mathcal{L}\bigg(y, \mathbb{E}(y\mid x)\bigg)^{\text{NOISE}} + \mathbb{E}_x\mathcal{L}\bigg[\mathbb{E}_X\mu(X)(x),\mathbb{E}(y\mid x)\bigg]^{\text{BIAS}} + \mathbb{E}_x\mathbb{E}_X\mathcal{L}\bigg\{\mu(X)(x),\mathbb{E}_X\mu(X)(x)\bigg\}^{\text{VARIANCE}}$$
Где под $\mu$ понимается конкретный метод обучения на [[Bootstrapping|бустрапе]] - суперсете выборок с повторениями: $\mu: (\mathbb{X}\times\mathbb{Y})^l\rightarrow \mathcal{A}$ - по факту, метод порождает из набора сэмплов с повторениями размера $l$ конкретную модель семейства $a \in \mathcal{A}$ 
___
### Noise|Шум
Характеристика задачи, независящая от самой модели, означает ошибку лучшей модели (в данном случае оптимум есть точечное усреднение $a_X(x)=\int_\mathbb{Y}y*p(Y|x)=\mathbb{E}(y\mid x)$), $\Rightarrow$ *константа, привязанная только к данным, потенциально, процедуре сбора и разметки, мера разрешимости и **обусловленности** задачи*

### Bias|Смещение
Оценка среднего отклонения моделей семейства от лучшей модели, по факту характеризующая богатство и экспрессивную мощность алгоритма $\Rightarrow$ *мера того, насколько модель семейства может приблизить идеальную, насколько вообще подходит для данных*

### Variance|Разброс
Показывает чувствительность модели к изменениям в обучающей выборке $\Rightarrow$ *в некотором смысле характеризует способность и склонность моделей семейства к переобучению на train*
___
*Source* 
-[[_src/Sokolov_HSE_ML_lectures20-21/lecture08-ensembles.pdf|lecture08-ensembles]]
-[[]]
