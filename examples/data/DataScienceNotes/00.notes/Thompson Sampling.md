---
tags:
  - STATS/BayessianInference
layer: bronze
---
Процедура онлайн инкрементального обучения для стохастической модели $q$ ([[aposterior]]) с параметрами $\theta$ распределенными по закону $p$ ([[prior]] модели)
___
for step in steps do:
{
*sample the model:*
    $\hat{\theta} \sim p$

*choose action and collect observation aftor application*
    $x_t \leftarrow argmax_{x\in\mathcal{X}}\mathbb{E}_{q_\hat{\theta}}\big[ r(y_t)|x_t = x)\big]$
    $y_t \leftarrow ENVIRONMENT(x_t)$

 *update parameters*
    $p \leftarrow\mathbb{P}_{p,q}(\theta|x_t, y_t)$
}
end for
___

Подразумевает максимизацию наград $r$ от действий.