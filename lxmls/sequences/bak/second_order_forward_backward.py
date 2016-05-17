import numpy as np


######
# Computes the forward backward trellis for a given sequence
# for a second order sequence
# N - Lenght of sequence
# H - Number of hidden states
# Receives:
# Node potentials (N,H) vector
# Edge potentials (N-1,H,H)
######
def forward_backward(node_potentials, edge_potentials):
    H, N = node_potentials.shape
    forward = np.zeros([H, N], dtype=float)
    backward = np.zeros([H, N], dtype=float)
    forward[:, 0] = node_potentials[:, 0]
    ## Forward loop
    for pos in range(1, N):
        for current_state in range(H):
            for prev_state in range(H):
                forward_v = forward[prev_state, pos - 1]
                trans_v = edge_potentials[prev_state, current_state, pos - 1]
                prob = forward_v * trans_v
                forward[current_state, pos] += prob
            forward[current_state, pos] *= node_potentials[current_state, pos]
    ## Backward loop
    backward[:, N - 1] = 1
    for pos in range(N - 2, -1, -1):
        for current_state in range(H):
            prob = 0
            for next_state in range(H):
                back = backward[next_state, pos + 1]
                trans = edge_potentials[current_state, next_state, pos]
                observation = node_potentials[next_state, pos + 1]
                prob += trans * observation * back
            backward[current_state, pos] = prob
    # sanity_check_forward_backward(forward,backward)
    return forward, backward


#########
## For every position - pos the sum_states forward(pos,state)*backward(pos,state) = Likelihood
#########
def sanity_check_forward_backward(forward, backward):
    H, N = forward.shape
    likelihood = np.zeros([N, 1])
    for pos in range(N):
        aux = 0
        for current_state in range(H):
            aux += forward[current_state, pos] * backward[current_state, pos]
        likelihood[pos] = aux
        for i in range(pos):
            if abs(aux - likelihood[i]) > 0.001:
                print(("Likelihood for pos %i and pos %i mismatch: %f - %f" % (i, pos, likelihood[i], aux)))
                return False

    return True
