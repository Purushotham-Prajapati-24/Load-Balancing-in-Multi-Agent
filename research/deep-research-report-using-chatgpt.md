# Dynamic Load Balancing for Heterogeneous MAS Task Scheduling

**Problem Setting:** We consider scheduling $N$ independent tasks on $M$ computational agents (machines) with different processing speeds $s_1,\dots,s_M$. Each task $j$ has a processing requirement $p_j$, so running it on agent $i$ takes time $p_j/s_i$.  The objective is to assign tasks to agents to minimize the *makespan* $C_{\max} = \max_i \sum_{j\in S_i} p_j/s_i$, where $S_i$ is the set of tasks assigned to agent $i$.  This is the classic scheduling problem on *related* (uniform) or *unrelated* machines.  Even in the simple case of identical machines ($s_i$ equal), minimizing makespan is strongly NP-hard (by reduction from 3-Partition)【54†L1-L4】.  In fact, Pinedo notes that $P||C_{\max}$ is strongly NP-hard【54†L1-L4】, so exact optimal scheduling (offline) is feasible only for small instances or special cases.  We therefore focus on designing **efficient approximate** algorithms.  

**Relevance to MAS:** In multi-agent systems (MAS), tasks must be allocated among agents to balance load.  The Contract Net Protocol (Smith, 1980) emphasizes that effective *resource allocation* means “balancing the computational load among the nodes”【53†L81-L89】.  Similarly, robotics and MAS research (e.g. Gerkey & Mataric 2004) formalizes task allocation (MRTA) as an optimization problem akin to scheduling【53†L81-L89】.  Thus, our scheduling model directly applies to MAS task sharing: each agent is a “machine” with a certain capacity, and tasks must be distributed to minimize completion time (max load)【53†L81-L89】.  As noted by Smith, solving this *connection problem* (task-to-agent assignment) is crucial for high performance and speedup【53†L81-L89】.

## Background and Related Work

**Scheduling Theory (Offline):**  For identical machines (uniform speeds), Graham’s List Scheduling (assign each job to the currently least-loaded machine) guarantees a makespan within a factor $2-\frac{1}{m}$ of optimum【51†L191-L194】.  If tasks are first sorted by descending size and then assigned greedily (LPT rule), the bound improves to $4/3 - \frac{1}{3m}$【51†L205-L209】.  These classic results (Graham 1966, 1969) give provable approximation ratios for off-line greedy algorithms.  For *unrelated machines* (fully heterogeneous), Lenstra–Shmoys–Tardos (1990) gave a 2-approximation via LP-rounding【3†L60-L64】, and proved no polynomial algorithm can achieve ratio $<3/2$ unless P=NP【3†L69-L72】.  Hochbaum & Shmoys (1987) showed that for *identical machines* one can do even better: a polynomial-time approximation scheme (PTAS) is possible when the number of machines $m$ is fixed【3†L60-L64】 (i.e. makespan can be made arbitrarily close to optimum).  However, in general $P||C_{\max}$ is strongly NP-hard【54†L1-L4】, so we rely on heuristics or pseudo-polynomial DP for small instances.

**Online Scheduling and Competitive Analysis:**  In the online setting, tasks arrive one by one (without future knowledge).  The standard performance measure is *competitive ratio*: the worst-case ratio of the online algorithm’s makespan to the offline optimum.  For identical machines, the simple greedy (list scheduling) algorithm is $(2-1/m)$-competitive【51†L191-L194】.  Later work improved this; e.g., Fleischer & Wahl (2000) gave a deterministic algorithm with competitive ratio approaching $1.9201$ as $m\to\infty$【16†L53-L57】.  However, for heterogeneous machines the guarantees are much worse.  In fact, classical results show any online algorithm for unrelated machines has a competitive ratio $\Omega(\log m)$ (and $\Omega(\log n)$ with $n$ jobs)【37†L12-L15】.  Best-known online algorithms achieve $O(\log n)$ competitive ratio in the most general (unrelated) setting【37†L36-L39】.  Thus in MAS with varied agent speeds, one cannot hope for a constant-factor online guarantee in the worst case – the competitive ratio grows logarithmically in system size.  Comprehensive surveys of online scheduling (Sgall 1998【46†L41-L49】, Azar 1998) confirm these bounds.  

**MAS Task Allocation:**  Multi-agent/task allocation literature (Gerkey & Mataric 2004; Korsah et al. 2013) classifies agent-task assignment problems (ST-SR-IA, etc) as analogous to scheduling or assignment problems【19†L45-L48】.  Decentralized protocols (e.g. Contract Net【53†L81-L89】) and market-based auctions have been used to allocate tasks by bidding【18†L548-L556】.  However, these often aim for social welfare or specific constraints; our focus is on minimizing makespan (max load) as in classical scheduling.  We thus build on scheduling theory (Graham, Lenstra, Hochbaum, etc.) while acknowledging the MAS context of distributed agents【53†L81-L89】【3†L60-L64】.

## Problem Formulation

We model $M$ agents as machines with speeds $s_1,\dots,s_M$.  There are $N$ tasks with processing requirements $p_1,\dots,p_N$.  The processing time of task $j$ on agent $i$ is $p_j/s_i$.  An *assignment* is a partition of tasks into sets $S_1,\dots,S_M$, one per agent.  The completion time of agent $i$ is $L_i = \sum_{j\in S_i} p_j/s_i$, and the makespan is $C_{\max} = \max_i L_i$.  Our **offline goal** is to find an assignment minimizing $C_{\max}$.  The **online setting** means tasks arrive in sequence (we must assign each upon arrival, without knowing future tasks).  We assume preemption is not allowed (each task must run to completion on one agent).

In MAS terms, this is load balancing on heterogeneous nodes: we wish to keep all agent loads even so that the maximum finish time is minimized.  Agents with higher speed (capacity) can handle more work.  Exact optimal scheduling is NP-hard【54†L1-L4】, so we design heuristic algorithms.

## Offline Scheduler (DP/Greedy)

### Algorithm (Greedy List Scheduling).  
A natural greedy algorithm (generalizing Graham’s LS) is as follows: 

1. **Sort tasks (optional):** If the full task list is known in advance, sort tasks in non-increasing order of $p_j$ (this is the LPT rule).  
2. **Initialize:** Set load $L_i=0$ for each agent $i$.  
3. **Assign tasks:** For each task $j$ (in sorted order for LPT, or arbitrary order for plain LS), compute its processing time on each agent $i$: $t_{ij}=p_j/s_i$.  Assign task $j$ to the agent $i^* = \arg\min_i (L_i + t_{ij})$ (the least-loaded after assignment).  Then update $L_{i^*} \leftarrow L_{i^*} + t_{i^* j}$.

This yields an offline schedule in $O(NM + N\log N)$ time (dominated by sorting).  In the identical-speed case ($s_i=1$), this is exactly LPT.  Graham’s analysis shows this schedule has makespan $C_{\max}\le (2-\frac{1}{M})\,C^*_{\max}$【51†L191-L194】 in general, and for LPT (sorted list) the bound improves to $4/3 - \frac{1}{3M}$【51†L205-L209】.  Thus even this simple greedy algorithm is a constant-factor approximation offline.  For heterogeneous speeds, one can transform by defining $p_{ij}=p_j/s_i$ and apply the same greedy rule; the worst-case ratio remains bounded (in fact identical to the identical-machines case in the speed-normalized metric)【51†L191-L194】【51†L205-L209】.

### Algorithm (Dynamic Programming).  
For small $N$, $M$ or special cases, one can solve optimally via dynamic programming.  For example, with $M=2$ this reduces to the partition problem (subset-sum DP) to split tasks into two loads as evenly as possible【54†L1-L4】.  More generally, one can use DP states that represent, say, how tasks are distributed among a prefix of machines or up to a guessed makespan $T$, but the state space grows exponentially.  A pseudo-polynomial DP can solve $P||C_{\max}$ exactly when $M$ is fixed (using 3-partition ideas【54†L1-L4】), but in practice such DP is feasible only for very small instances due to NP-hardness【54†L1-L4】.  Thus DP is mainly of theoretical interest or a brute-force subroutine for benchmarking.

In summary, our offline scheduler uses the LPT-like greedy rule, which is simple to implement and has provable approximation bounds (see above).  For very small cases we note DP is possible but not scalable.

## Online Scheduler (Greedy Load Balancing)

In the online scenario, tasks arrive one by one and must be assigned immediately.  We use **List Scheduling**: upon arrival of a task $j$, compute $t_{ij}=p_j/s_i$ for each agent $i$, then assign $j$ to the agent $i^*$ that minimizes the resulting load $L_i + t_{ij}$.  (Initially $L_i=0$.)  This requires $O(M)$ work per task.  No sorting is done since future tasks are unknown.  This algorithm is essentially a greedy load-balancer: always place the incoming job on the machine that will finish it earliest.

In identical machines ($s_i=1$), this is exactly Graham’s online List Scheduling.  Its competitive ratio is well-known: $C_{\max}^{\rm online} \le (2-\frac{1}{M})\,C^*_{\max}$【51†L191-L194】.  If instead we could sort tasks offline (LPT), the ratio improves to $4/3-1/(3M)$【51†L205-L209】, but online we cannot sort unknown future jobs.  For heterogeneous speeds, the same greedy rule is applied, but the worst-case performance degrades.  Indeed, classical results show that *no* online algorithm can have a constant competitive ratio across all instances when machines are unrelated or even uniformly related (varying $s_i$) – the ratio grows logarithmically.  In particular, Azar *et al.* (1997) and follow-up work prove $\Omega(\log M)$ lower bounds on any online algorithm’s competitive ratio when machines differ【37†L12-L15】.  Our greedy policy then has competitive ratio $O(\log n)$ in the worst case, matching the best known bounds【37†L36-L39】. 

We summarize the guarantees:
- **Identical machines:** Online greedy (LS) is $(2-1/M)$-competitive【51†L191-L194】. Offline LPT is $(4/3-1/(3M))$-approximate【51†L205-L209】.
- **Heterogeneous machines:** Offline greedy still yields a bounded approx (by transformation to normalized loads【51†L191-L194】), but online greedy can be as bad as logarithmic.  In fact, no online rule beats $O(\log n)$ competitive ratio in general【37†L36-L39】 (Aspnes *et al.*, 1997). 

## Algorithm Details

Below is pseudocode for the online scheduler:

```
Initialize L[i] = 0 for all agents i=1..M.
For each arriving task j (with size p_j):
    For each agent i compute time t_i = p_j / s_i.
    Let i* = argmin_i (L[i] + t_i).
    Assign task j to agent i*; update L[i*] += t_{i*}.
```

Key properties:
- **Greedy:** always picks the current least-loaded agent (in finish time).  
- **Speed-aware:** naturally places longer tasks on faster machines because $t_i = p_j/s_i$ is smaller for larger $s_i$.  

This algorithm is simple and requires only $O(M)$ work per task.  It does not rebalance or migrate tasks.  

For **offline** scheduling (all tasks known), we would first sort tasks by $p_j$ descending and then use the same assignment loop.  That yields LPT and has the better ratio $4/3-1/(3M)$【51†L205-L209】.

## Theoretical Analysis

**Offline (Approximation Bounds):** By standard scheduling bounds, our offline LPT-based schedule satisfies 
\[
C_{\max}^{\rm LPT} \;\le\; \Bigl(\frac{4}{3} - \frac{1}{3M}\Bigr)\,C^*_{\max},
\] 
and even the unsorted greedy satisfies 
\[
C_{\max}^{\rm LS} \;\le\; \Bigl(2-\frac{1}{M}\Bigr)\,C^*_{\max},
\] 
where $C^*_{\max}$ is the true optimum makespan【51†L191-L194】【51†L205-L209】.  These follow from Graham’s classic analysis.  (We omit the detailed proof here, but it hinges on the fact that when the last job completes, no machine can exceed $C_{\max}^{\rm LPT}+p_{\max}$ where $p_{\max}$ is the largest job, leading to the $4/3$ bound.)  Hence offline our greedy scheduler is a constant-factor approximation.  

**Online (Competitive Analysis):** In the online case, we compare our greedy makespan to $C^*_{\max}$ that an offline omniscient scheduler would achieve.  For identical machines, Graham’s bound still applies, yielding a competitive ratio of $2-1/M$【51†L191-L194】.  However, when machines have unequal speeds, known lower bounds show no online algorithm can have constant ratio【37†L12-L15】.  In fact, Azar *et al.* (1997) proved that any online algorithm on unrelated machines has competitive ratio at least $\Omega(\log M)$, and there are matching $O(\log n)$-competitive algorithms【37†L36-L39】.  Our greedy algorithm is essentially one of the simplest deterministic strategies, so it will achieve $O(\log n)$ competitive ratio in the worst case (e.g., adversarial inputs can force an $\Theta(\log n)$ blowup).  We do not attempt to beat this bound here; rather, we note that our strategy is within constant factors of the best possible (up to logarithmic factors) in general heterogeneous settings【37†L12-L15】【37†L36-L39】.  

In summary, the online greedy scheduler has constant competitive ratio for identical machines but only logarithmic ratio for general heterogeneous machines (which is unavoidable).  Quantitatively:
- Identical ($s_i=1$): $C_{\max}^{\rm online} \le (2-\frac{1}{M})\,C^*_{\max}$【51†L191-L194】.  
- Related/unrelated: $C_{\max}^{\rm online} = O(\log n)\,C^*_{\max}$ in worst case【37†L36-L39】.

These competitive bounds formalize the trade-off between online simplicity and optimal performance.  

## Evaluation Plan

To evaluate our scheduler, we will implement both the online greedy algorithm and an offline baseline.  The **offline optimal** can be approximated via an ILP solver or specialized PTAS (for small instances) to get $C^*_{\max}$ for comparison.  We can also test the greedy LPT schedule (offline greedy) as a benchmark.  Our test scenarios will include:
- Random task lengths (e.g. uniform or power-law distributions) for $N$ up to a few hundred.
- Agent speeds sampled from a distribution (e.g. some fast, some slow machines).
- Evaluate both online assignment (simulate tasks arriving one by one) and offline (all tasks known).
- Measure the makespan achieved, and compute the empirical ratio $C_{\max}^{\rm alg}/C_{\max}^*$.  

We expect results consistent with theory: for identical/similar speeds, the greedy will be within a factor $\le 2$ of optimum, while for highly heterogeneous speeds adversarial sequences may incur larger ratios (logarithmic in $n$).  We will also compare against trivial baselines (e.g. round-robin, random assignment) to show the benefit of the greedy rule.

## References

We built on classical scheduling theory (Graham 1966, 1969【51†L191-L194】【51†L205-L209】) and MAS task allocation literature【53†L81-L89】. Key algorithmic results we use include the $2$-approximation for unrelated machines【3†L60-L64】 and competitive analysis bounds【37†L12-L15】【37†L36-L39】.  The NP-hardness of makespan scheduling is documented in Garey–Johnson【54†L1-L4】.  Comprehensive discussions of these topics can be found in Pinedo’s scheduling text and surveys (e.g. Sgall 1998) and in MAS surveys【53†L81-L89】【3†L60-L64】. 

