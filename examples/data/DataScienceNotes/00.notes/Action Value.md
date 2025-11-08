---
tags:
  - RL
layer: bronze
---
Action Value *(action-state value)* $q$ - часть в разложении обычного [[RL парадигма#Value|value]] *(state value)* :
$$v_{\pi}(a|s) = \mathbb{E}_{\pi}\big[G_t |S_t = s\big] = \sum_{a \in \mathcal{A}}\mathbb{E}_{\pi}\big[G_t |S_t = s, A_t = a\big]*\pi(a|s) = \sum_{a \in \mathcal{A}}q(a,s)*\pi(a|s)$$
![[action_state_valuse.png]]
По факту $q$ фиксирует степень свободы выбора действия $a$ и оценивает матожидание returns.

Также рассмотрение формулы value дает разложение:
$$v_{\pi}(s) = \sum_{a \in \mathcal{A}}\pi(a,s)*\bigg[ \sum_{r \in \mathcal{R}} p(r|s,a)*r + \gamma\sum_{s' \in \mathcal{S}}p(s'|s,a)v_{\pi}(s')\bigg]; \text{}v_{\pi}(s')  \text{ рекурсивно содержит в себе } \gamma^{j}$$
$$\Downarrow$$
$$q(a,s) = \sum_{r \in \mathcal{R}} p(r|s,a)*r + \gamma\sum_{s' \in \mathcal{S}}p(s'|s,a)v_{\pi}(s') \Rightarrow q(a,s) = \overline{r_{\text{Imediate}}} + \overline{r_{\text{Discounted Future}}}$$
То есть action value есть сумма средней мгновенной награды и средней дисконтированной будущей.