Zero-Knowledge Interactive Protocol for Subgraph Isomorphism
============================================================
1. Problem Statement:
---------------------

Prover (Peggy) and Verifier (Victor) have graphs G1 and G2.
The Prover also knows a graph G' which is a subgraph of G2 and the isomorphism, pi, between G1 and G'.
The Prover must convince the Verifier of his/her knowledge of the subgraph isomorphism without
making it any easier for the Verifier to find either G' or its isomorphism with G1.

G1 <--- (isomorphism: pi) ---> G' <---- (subgraph of) -- G2
^                              ^                          ^
|                              |                          |
|                              |                          |
|                    (isomorphism: alpha')        (isomorphism: alpha)
|                              |                          |
|                              |                          |
|                              v                          v
------->(isomorphism: pi')---> Q' <---- (subgraph of) --- Q

2. Implementation:
------------------

The code consists of two separate processes, a prover process and the verifier process.
The processes communicate using named pipes. Both the prover and the verifier have 
access to a common file which contains the adjacency matrices for the graph G1 and G2.
The prover aditionally has access to a file which contains 
  a) a subgraph inducer, that specifies a set of edge removals (ER) and vertex deletion (VD) that produce the graph G' from G2.
  b) the isomorphism between G1 and G', called as pi_original.
In the code the isomorphism pi is referred to as pi_original while the isomorphism pi' is simply referred as pi.
The isomorphism is specified as a list such that j = pi_original[i] where vertex i in G' maps to vertex j in graph G1.
The bulk of the logic for computing isomorphisms is contained in process module, while 
the bit (graph) commitment logic is contained in the commitment module.

The veifier communicates to the prover the number of iterations for which it wants to run the protocol.
In each iteration the prover and verifier engage in the following protocol:
1) The prover generates a random isomorphism, alpha, and applies the permutation to G2 to produce the graph Q.
  The permutation alpha is a list which specifies the mapping between the vertices of G2 and Q. If we consider G1, G2, Q and 
  other graphs as adjacency matrices then Q[alpha[i]][alpha[j]] = G2[i][j].
2) The prover then commits to the graph Q and sends the commitment to the verifier.
3) The verifier then tosses a coin and then sends the outcome of the toss to the prover.
4) Depending on the outcome of the toss, the prover does one of the following:
  a) If the result is Heads (H) then the prover reveals the commitment to the verifier and also the permutation alpha.
  b) If the result is Tails (T) then the verifier computes the permutation pi' (called pi in code) between G1 and Q'.
     The prover first computes the isomorphism, alpha', between G' and Q' which is nothing but the permutation alpha
     applied on a subset of vertices. Now if a vertex i of G1 maps to vertex j of G' and the vertex j maps to vertex k of
     Q' then vertex i of G1 maps to vertex k of Q' and thus pi'[i] = k. So the Prover computes the permutation pi'.
     The prover then sends the permutation pi' and reveals only part of the adjacency matrix of Q that contains the
     subgraph Q'.
5) The verifier does one of the following:
  a) If the outcome was Heads, then the verifier applies the permutation alpha to G2 and ensures that
     the result matches with Q which was revealed by the prover.
  b) The verifier applies the permutation pi' to G1 and ensures that the result matches with the subgraph 
     that was revealed by the prover.

If all the iterations complete successfully then the verifier is convinced of prover's knowledge of the isomorphism 
between G1 and G'.

Additionally, both the prover and verifier write transcripts of all the iterations so that correctness of the code can be verified.



