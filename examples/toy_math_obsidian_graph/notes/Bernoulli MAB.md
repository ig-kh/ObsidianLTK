---
tags:
  - RL/Bandits
  - SYS/DEPRECATED
---
$$\boxed{\hat{\theta}_{k,t} \leftarrow \frac{\alpha_{k,t}}{\alpha_{k,t}+\beta_{k,t}}}$$
Бандиты Бернулли являются частным случаем [[Multi-Armed Bandit|MAB]] для всех ручек которого $r_k\in\{0,1\}$, реализуя таким образом схему Бернулли, где каждая ручка параметризована $\theta_k=p_k=\mathbb{P}(r_k=1)$ и соотв. неявным $q_k=1-p_k=\mathbb{P}(r_k=0)$

Бернули бандит в явном виде является дважды жадным:
1) Стандртный  подход к выбору действия [[Greedy & ɛ-Greedy Action Value-based MAB|по аргмаксу]] - $A_{k,t}=argmax_{A_k\in\mathcal{A}}\hat{\theta}_{k,t}$
2) Жадная оценка параметра: пусть $\alpha_{k,t}$ - число 1 к моменту $t$ от действия $k$, а $\beta_{k,t}$ - число 0, тогда  оценка $\hat{\theta}_{k,t} = \mathbb{E}_{\mathbb{H}_t}[{p_k}] = \mathbb{E}_{\mathbb{H}_t}\big[\mathbb{P}(r_k=1)\big]$ как **матожидание** вероятности 1,  в силу распределения наград это матожидание есть отношение количества 1 ко всем исходам: $\hat{\theta}_{k,t} = \frac{\alpha_{k,t}}{\alpha_{k,t}+\beta_{k,t}}$

Обновление параметров $\alpha/\beta$ для каждого действия при выборе логично происходит как
$$(\alpha_{k,t+1},\beta_{k,t+1}) \leftarrow (\alpha_{k,t} + r_t,\beta_{k,t}+1-r_t)$$
То есть только $\alpha$ или только $\beta$ поменяются на единицу в зависимости от награды.