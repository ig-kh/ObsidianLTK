---
tags:
  - RL/PG
layer: bronze
---
#### Оценка Монте Карло градиента
$$\theta_{t+1} \leftarrow \theta_t + \alpha\nabla_{\theta}\mathcal{J}(\theta_t) = \theta_t + \alpha\mathbb{E}\big[ \nabla_{\theta}\ln\pi_{\theta_t}(A|S)q_{\pi_{\theta_t}}(A,S)\big]$$
$$\Downarrow$$
Истинное значение [[Natural Policy Gradient|градиента]] не известно, используется оценка Монте Карло $q_{\pi} \approx q_t$ (если MC est., то метод - MCPG):
$$\Downarrow$$
$$\theta_{t+1} \leftarrow \theta_t + \alpha \nabla_{\theta}\ln\pi_{\theta_t}(a_t|s_t)q_{t}(a_t,s_t)$$

