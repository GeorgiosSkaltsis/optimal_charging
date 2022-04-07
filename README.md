##  Introduction
The task of optimal charging of an EV can be formulated as a Linear Programming (LP)   problem. In the following we present four different smart charging algorithms for EVs. Specifically, we formulate the problem for
- cost-optimal charging given a price forecast of a real-time market,
- fast-as-possible charging,
- a multi-objective optimization scheme that finds a trade-off between cost-optimal and fast-as-possible,
- an example for Vehicle-to-Grid (V2G) charging strategy.


## Electric Vehicle model
With respect to charging, an EV behaves as a battery storage. As a result, the parameters that describe its charging behavior are the maximum storage capacity $`E_{max}^{ess}`$, the maximum charging power $`P_{max}^{ess}`$, the charging loss rates $`\eta_{in}`$ and $`\eta_{out}`$ and the minimum state of charge $`SOC_{min}`$. The charging behavior is modeled by the following constraints.

```math
E_{t}^{e s s} =E_{0}^{e s s}+\sum_{\tau=1}^{t} \eta_{i n} P_{\tau}^{e s s, i n}-\sum_{\tau=1}^{t} \frac{1}{\eta_{o u t}} P_{\tau}^{e s s, o u t},  \\
E_{t}^{e s s}  \leq E_{max}^{ess}, \\
E_{t}^{e s s}  \geq SOC_{min}\cdot E_{max}^{ess},\\
P_{t}^{e s s, o u t} \leq P_{max}^{ess} ; \quad P_{t}^{e s s, in} \leq P_{max}^{ess},\\
P_{t}^{e s s, o u t}; P_{t}^{e s s, in}; E_{t}^{e s s} \geq 0,
```
$` \forall t \in \{1,\dots,T\}`$, where $`P_{t}^{e s s, i n}`$, $`P_{t}^{e s s, out}`$ and $`E_{t}^{e s s}`$ are the decision variables. Moreover, $`E_{0}^{e s s}`$ is the energy stored in the EV initially and $`T`$ is the number of time slots of the charging time horizon.

## Cost-optimal charging policy
Assume that the smart charger provides energy with time varying prices. Usually, in real-time markets the prices are not known in advance, yet we can reasonably assume that there is a price forecast denoted as $`p_t`$ for $`t \in \{1,\dots,T\}`$. Then, for an EV that arrives with initial state of charge $`E_{0}`$ and aims to reach a final state of charge $`\alpha\in (SOC_{min},1]`$ within $`T`$ time slots, the cost-optimal charging problem is formulated as 
```math
minimize \quad \sum_{t=1}^{T} P_{t}^{e s s, i n} \cdot p_{t} \\
\text{s.t.} \quad E_{t}^{e s s} =E_{0}^{e s s}+\sum_{\tau=1}^{t} \eta_{i n} P_{\tau}^{e s s, i n}, \\
E_{T}^{e s s}  = \alpha \cdot E_{max}^{ess},  \\
E_{t}^{e s s}  \leq E_{max}^{ess},  \\
E_{t}^{e s s}  \geq SOC^{min}\cdot E_{max}^{ess}, \\
P_{t}^{e s s, in} \leq P_{max}^{ess},\\
P_{t}^{e s s, in}; E_{t}^{e s s} \geq 0,
```
where $`p_t`$ denotes the forecasted electricity price for each time slot. It should be noted that in this case V2G is not considered and for that $`P_{t}^{e s s, out}`$ is not included in the constraints of the EV model. Assume that the forecasted prices in the real-time market are the ones illustrated in the following figure.
![prices](https://user-images.githubusercontent.com/25156570/158619424-c19f66f0-d16d-4578-b768-68587d8e7948.png)


Then, for an EV with parameters $`E_{max}^{ess}=15kWh`$, $`P_{max}^{ess}=9kW`$, $`\eta_{in}=0.9`$, $`E_{0}^{e s s}=4.5kWh`$ that aims to go fully charged within 4 hours, that is $`T=16`$ since time resolution is 15 minutes, the cost-optimal charging policy is the one illustrated in the following figure.
![cost_optimal](https://user-images.githubusercontent.com/25156570/158619451-8992d20f-4059-4dae-923f-2f364f82ebe9.png)


As expected, it can be noticed that the EV charges, that is $`P_{t}^{e s s, i n}`$ is positive, at the time slots in which electricity prices are expected to be cheap. For this case, the duration of charging is 225 minutes and the electricity cost is equal to $`0.83`$ euros.

## Fast-as-possible charging

Very often it might be the case that an EV driver is in a hurry and needs to charge its vehicle as fast as possible. To tackle this problem we should re-formulate the objective function of the optimization scheme so that it is not oriented towards reducing cost, and instead prioritize the minimization of charging time. In practice it is not feasible (at least not in a straight forward manner) to minimize the charging time per se. Instead, in order to facilitate the formulation of the fast-as-possible charging problem we can create virtual market prices that penalize future consumption. That is, we create an ancillary virtual price forecast denoted as $`p^{virtual}_t \leftarrow \text{array of increasing values}`$ and then the problem is formulated as follows.

```math
minimize \quad \sum_{t=1}^{T} P_{t}^{e s s, i n} \cdot p^{virtual}_t \\
\text{s.t.} \quad E_{t}^{e s s} =E_{0}^{e s s}+\sum_{\tau=1}^{t} \eta_{i n} P_{\tau}^{e s s, i n}, \\
E_{T}^{e s s}  = \alpha \cdot E_{max}^{ess},  \\
E_{t}^{e s s}  \leq E_{max}^{ess},  \\
E_{t}^{e s s}  \geq SOC^{min}\cdot E_{max}^{ess}, \\
P_{t}^{e s s, in} \leq P_{max}^{ess},\\
P_{t}^{e s s, in}; E_{t}^{e s s} \geq 0,
```
and the resulting charging policy, considering initial parameters to be same as previously, turns out to be as illustrated in the following figure, with total charging period being 90 minutes and electricity cost equal to $`1.45`$ euros.
![minimum_time](https://user-images.githubusercontent.com/25156570/158619516-597df812-60fd-401f-93d5-969e6fdafd3d.png)



## Multi-objective charging policy

In the previous two cases cost-optimal and fast-as-possible charging policies were examined. However, a cost-optimal strategy might often take too long for charging and a fast-as-possible strategy might be too expensive. As a result, it is worth examining a charging policy that aims to find a trade-off between cost and charging time. In order to facilitate the formulation of this problem we, once again, need to employ an ancillary virtual price forecast denoted as $`p^{virtual}_t \leftarrow \text{array of increasing values}`$. Then, the problem is formulated as follows.

```math
minimize \quad \sum_{t=1}^{T} \left[ P_{t}^{e s s, i n} \cdot (p_t + p^{virtual}_t) \right] \\
\text{s.t.} \quad E_{t}^{e s s} =E_{0}^{e s s}+\sum_{\tau=1}^{t} \eta_{i n} P_{\tau}^{e s s, i n}, \\
E_{T}^{e s s}  = \alpha \cdot E_{max}^{ess},  \\
E_{t}^{e s s}  \leq E_{max}^{ess},  \\
E_{t}^{e s s}  \geq SOC^{min}\cdot E_{max}^{ess}, \\
P_{t}^{e s s, in} \leq P_{max}^{ess},\\
P_{t}^{e s s, in}; E_{t}^{e s s} \geq 0,
```
Naturally, how the optimization designer initializes the virtual prices $`p^{virtual}_t`$, that penalize future consumption, is important for the resulting charging policy. Specifically, the higher $`p^{virtual}_t`$ are next to  $`p_t`$ the more fast-charging will be prioritized over cheap-charging. For $`p^{virtual}_t`$ being initialized as 

```python
market_prices= pd.read_csv ('prices_example.csv') # p_t forecasted prices
max_number_of_intervals = 16
offset = min(market_prices)
step = max(market_prices) / max_number_of_intervals
num = max_number_of_intervals
auxiliary_array = np.arange(0,num) * step + offset # p_virtual_t prices
```
and with charging parameters being as described previously, the charging policy for multi-objective optimization is as presented in the following figure, with total charging period being 135 minutes and electricity cost equal to $`1.07`$ euros. 
![multi_objective](https://user-images.githubusercontent.com/25156570/158619551-10b0a6d6-872a-4c8e-917e-1ae15380e5db.png)


## V2G smart charging

It is often desired to additionally consider the ability of an EV to provide energy to the grid in times that this is necessary. For tackling a general case of such a problem, let us assume that an EV, similar to the one of the previous cases, arrives at a smart charger and needs to be fully charged in 4 hours. Given this restriction, the smart charger is responsible to take optimal decisions with respect to charging and discharging in order to reduce the expected cost. This problem is formulated as

```math
minimize \quad \sum_{t=1}^{T} \left[ (P_{t}^{e s s, i n} - P_{t}^{e s s, out}) \cdot p_t \right] \\
\text{s.t.} \quad E_{t}^{e s s} =E_{0}^{e s s}+\sum_{\tau=1}^{t} \eta_{i n} P_{\tau}^{e s s, i n}-\sum_{\tau=1}^{t} \frac{1}{\eta_{o u t}} P_{\tau}^{e s s, o u t}, \\
E_{T}^{e s s}  = \alpha \cdot E_{max}^{ess},  \\
E_{t}^{e s s}  \leq E_{max}^{ess},  \\
E_{t}^{e s s}  \geq SOC^{min}\cdot E_{max}^{ess}, \\
P_{t}^{e s s, in} \leq P_{max}^{ess}; P_{t}^{e s s, out} \leq P_{max}^{ess},\\
P_{t}^{e s s, in};P_{t}^{e s s, out}; E_{t}^{e s s} \geq 0,
```
with $`\alpha=1.0`$. Assuming that $`\eta_{out}=0.9`$ and considering the same forecasted prices $`p_t`$ as before, the V2G optimization is as presented in the following figure. 
![v2g](https://user-images.githubusercontent.com/25156570/158619582-abd745f1-7432-4515-87a9-c1ce841a3d95.png)

The corresponding charging period is 240 minutes, that is 4 hours as expected, and the electricity cost is equal to $`0.4`$ euros. Naturally, for longer charging periods the V2G strategy will result to profits. It should be noted that if selling and buying prices to and from the grid are different then the objective function should be expressed as $`\sum_{t=1}^{T} \left[ P_{t}^{e s s, i n}  \cdot p^{buying}_t - P_{t}^{e s s, out} \cdot p^{selling}_t \right]`$.

## Comparison

In the following figure one can see a comparison between the different charging policies presented previously, together with the corresponding charging periods and costs of electricity.
![comparison](https://user-images.githubusercontent.com/25156570/158619628-c28b4111-afcf-4876-afcd-2afc8de03346.png)



