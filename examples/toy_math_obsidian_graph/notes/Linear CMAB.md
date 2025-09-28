---
tags:
  - RL/Bandits
  - SYS/DEPRECATED
---
$$\boxed{Q_t(a) = x_t^T\theta_{a,t}}$$
Линейный [[Contextual MAB|контекстуальный бандит]] действует в рамках предположения о линейности награды от контекста:
$$Q_t(a) = x_t^T\theta_{a,t}: \theta_{a,t} = A_{a,t}^{-1}b_{a,t},\text{ где } A_{a,t}\approx Cov[\mathcal{X}], b_{a,t}\approx\overline{\mathcal{X}}$$
В отличии от прямых методов инкрементальное обновление оценки награды, обновляются параметры оценки $Update_{R_{t+1}}(Q_t(a)) \rightarrow Update_{R_{t+1}}(\theta_t(a))$.
Для выбранного действия:
$$A_{a,t} \leftarrow A_{a, t-1}+x_tx_t^T$$
$$b_{a,t} \leftarrow b_{a,t-1}+x_tr_{a,t}$$
Для остальных действий в disjoint случае обновление просто не происходит.