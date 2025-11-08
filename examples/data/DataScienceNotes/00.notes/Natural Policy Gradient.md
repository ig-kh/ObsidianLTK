---
tags:
  - RL/PG
layer: bronze
---
#### Policy Gradient Ascend
Пусть есть некоторая скалярная метрика качества агента, действующего с параметризованной [[RL парадигма#Policy|политикой]] $\pi_{\theta}$, $\mathcal{J}(\theta)$.
Отыскание оптимальной политики - параметров политики в соответствии с метрикой возможно методом градиентного подъема:
$$\theta_{t+1} \leftarrow \theta_t + \nabla_{\theta}\mathcal{J}(\theta_{t})$$
#### Оптимизируемая метрика
В качестве метрики рассматриваются *average state value* $\overline{v}_{\pi}$ и *avereage (one-step) reward* $\overline{r}_{\pi}$ 

$$\overline{v}_{\pi_{\theta}} \leftarrow \mathcal{J}(\theta) \rightarrow \overline{r}_{\pi_{\theta}}$$
___
$$\overline{v}_{\pi} = \sum_{s\in\mathcal{S}}d(s)v_{\pi}(s)=\mathbb{E}_{s\sim d}[v_{\pi}(s)] = \lim_{n\rightarrow\infty}\mathbb{E}\bigg[ \sum_{t=0}^n\gamma^tR_{t+1}\bigg]$$
___
$$\overline{r}_{\pi} = \sum_{s\in\mathcal{S}}d_{\pi}(s)r_{\pi}(s) = \mathbb{E}_{S\sim d_{\pi}}\big[r_{\pi}(S)\big]=\lim_{n\rightarrow \infty}\frac{1}{n}\mathbb{E}\bigg[\sum_{t=0}^{n-1} R_{t+1}\bigg]$$
___
$d(s), d_\pi(s)$ рассматриваются как стационарные распределения состояний мира, зависящие или не зависящие от политики $\pi$ и от изначального состояния $d^0$. 

В общем случае с дисконтированием будущих наград $\gamma \lt 1$  имеет место (по последним версиям определений) равенство $\overline{r}_\pi = (1-\gamma)\overline{v}_\pi$, то есть со-направлены вектора роста. 

Что подводит нас к...
#### Градиент метрик
Так в случаях $\gamma \lt 1$ и $\gamma \geq 1$, $d$ и $d_\pi$, градиенты $\mathcal{J}(\theta)$ равного $\overline{r}_\pi$ и $\overline{v}_{\pi}$ [[Mathematical foundations of reinforcement learning.pdf#page=214|могут быть выражены как приближение или точное значение]] через [[Action Value|action-vcalue]] следующим образом:
$$\nabla_{\theta}\mathcal{J}(\theta) = \sum_{s \in \mathcal{S}}\eta(s)\sum_{a\in\mathcal{A}}\nabla_{\theta}\pi_{\theta}(a|s)q_{\pi_{\theta}}(a,s) = \mathbb{E}_{S\sim\eta, A\sim\pi_{\theta}(S)}\bigg[\nabla_{\theta}\ln\pi_{\theta}(A|S)q_{\pi_{\theta}}(A,S) \bigg]; \eta(s) \equiv d(s), d_\pi(s)$$
Что называется  основной теоремой градиента политики.