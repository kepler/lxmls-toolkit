#!/usr/bin/python

import os
# import urllib.request, urllib.error, urllib.parse
from six.moves import urllib
import numpy as np
import theano
import theano.tensor as T


# from ipdb import set_trace

def download_embeddings(embbeding_name, target_file):
    """
    Downloads file through http with progress report

    Obtained in stack overflow:
    http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http
    -using-python
    """

    # Embedding download URLs
    if embbeding_name == 'senna_50':
        # senna_50 embeddings
        source_url = 'http://lxmls.it.pt/2015/wp-content/uploads/2015/senna_50'
    else:
        raise ValueError("I do not have embeddings %s for download"
                         % embbeding_name)

    target_file_name = os.path.basename('data/senna_50')
    u = urllib.request.urlopen(source_url)
    with open(target_file, 'wb') as f:
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_dl = 0
        block_sz = 8192
        print("Downloading: %s Bytes: %s" % (target_file_name, file_size))
        while True:
            text_buffer = u.read(block_sz)
            if not text_buffer:
                break
            file_size_dl += len(text_buffer)
            f.write(text_buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl,
                                           file_size_dl * 100. / file_size)
            status += chr(8) * (len(status) + 1)
            print(status,)
    print("")


def extract_embeddings(embedding_path, word_dict):
    """
    Given embeddings in text form and a word dictionary construct embedding
    matrix. Words with no embedding get initialized to random.
    """

    with open(embedding_path) as fid:
        for i, line in enumerate(fid.readlines()):
            # Initialize
            if i == 0:
                N = len(line.split()[1:])
                E = np.random.uniform(size=(N, len(word_dict)))
                n = 0
            word = line.split()[0].lower()
            if word[0].upper() + word[1:] in word_dict:
                idx = word_dict[word[0].upper() + word[1:]]
                E[:, idx] = np.array(line.strip().split()[1:]).astype(float)
                n += 1
            elif word in word_dict:
                idx = word_dict[word]
                E[:, idx] = np.array(line.strip().split()[1:]).astype(float)
                n += 1
            print("\rGetting embeddings for the vocabulary %d/%d" % (n, len(word_dict)),)
    OOV_perc = (1 - n * 1. / len(word_dict)) * 100
    print("\n%2.1f%% OOV, missing embeddings set to random" % OOV_perc)
    return E


class NumpyRNN:
    def __init__(self, W_e, n_hidd, n_tags, seed=None):
        """
        E       numpy.array Word embeddings of size (n_emb, n_words)
        n_hidd  int         Size of the recurrent layer
        n_tags  int         Total number of tags
        seed    int         Seed to random initialization of parameters (default=None)
        """
        # Dimension of the embeddings
        n_emb = W_e.shape[0]

        # MODEL PARAMETERS
        np.random.seed(seed)
        W_x = np.random.uniform(size=(n_hidd, n_emb))  # Input layer
        W_h = np.random.uniform(size=(n_hidd, n_hidd))  # Recurrent layer
        W_y = np.random.uniform(size=(n_tags, n_hidd))  # Output layer

        # Class variables
        self.n_hidd = n_hidd
        self.param = [W_e, W_x, W_h, W_y]
        # self.param_names  = ['W_e', 'W_x', 'W_h', 'W_y']
        self.activation_function = 'logistic'  # 'tanh' 'relu' 'logistic'

    def apply_activation(self, x, function_name):
        """
        """
        if function_name == 'logistic':
            z = 1 / (1 + np.exp(-x))
        elif function_name == 'tanh':
            z = np.tanh(x)
        elif function_name == 'relu':
            z = x
            ind = np.where(z < 0.)
            z[ind] = 0.
        else:
            raise NotImplementedError
        return z

    def derivate_activation(self, z, function_name):
        """
        """
        if function_name == 'logistic':
            dx = z * (1. - z)
        elif function_name == 'tanh':
            dx = (1. - z * z)
        elif function_name == 'relu':
            dx = (np.sign(z) + 1) / 2.
        else:
            raise NotImplementedError
        # pdb.set_trace()
        return dx

    @staticmethod
    def soft_max(x, alpha=1.0):
        """
        """
        e = np.exp(x / alpha)
        return e / np.sum(e)

    def forward(self, x, allOuts=False, outputs=None):
        """
        Forward pass

        allOuts = True  return intermediate activations; needed to comput backpropagation
        """
        # Get parameters in nice form
        if outputs is None:
            outputs = []
        W_e, W_x, W_h, W_y = self.param

        z1, h, y, p, p_y = {}, {}, {}, {}, {}
        h[-1] = np.zeros(self.n_hidd)
        loss = 0.
        for t in range(len(x)):

            z1[t] = W_e[:, x[t]].T

            h[t] = self.apply_activation(W_x.dot(z1[t]) + W_h.dot(h[t - 1]),
                                         self.activation_function)

            y[t] = W_y.dot(h[t])

            ymax = max(y[t])
            logsum = ymax + np.log(sum(np.exp(y[t] - ymax)))
            p[t] = np.exp(y[t] - logsum)
            p_y[t] = p[t] / np.sum(p[t])  ##  
            #            # Annother way of computing p_y[t]
            #            p_y[t] = self.soft_max(y[t])

            if outputs:
                loss += -np.log(p_y[t][outputs[t]])  # Cross-entropy loss.

        loss /= len(x)  # Normalize to get the mean

        if allOuts:
            return loss, p_y, p, y, h, z1, x
        else:
            return p_y

    def grads(self, x, outputs):
        """
            Compute gradientes, with the back-propagation method
            inputs:
                x: vector with the (embedding) indicies of the words of a sentence
                outputs: vector with the indicies of the tags for each word of the sentence
            outputs:
                nabla_params: vector with parameters gradientes
        """

        # Get parameters
        W_e, W_x, W_h, W_y = self.param

        loss, p_y, p, y, h, z1, x = self.forward(x, allOuts=True, outputs=outputs)

        # Initialize gradients with zero entrances
        nabla_W_e = np.zeros(W_e.shape)
        nabla_W_x = np.zeros(W_x.shape)
        nabla_W_h = np.zeros(W_h.shape)
        nabla_W_y = np.zeros(W_y.shape)

        # backward pass, with gradient computation
        dh_next = np.zeros_like(h[0])
        for t in reversed(range(len(x))):
            dy = np.copy(p[t])
            dy[outputs[t]] -= 1.  # backprop into y (softmax grad).
            nabla_W_y += dy[:, None].dot(h[t][None, :])

            dh = W_y.T.dot(dy) + dh_next  # backprop into h.
            # backprop through nonlinearity.
            dh_raw = self.derivate_activation(h[t], self.activation_function) * dh

            nabla_W_h += dh_raw[:, None].dot(h[t - 1][None, :])

            nabla_W_x += dh_raw[:, None].dot(z1[t][None, :])

            d_z1 = W_x.T.dot(dh_raw)

            nabla_W_e[:, x[t]] += d_z1

            dh_next = W_h.T.dot(dh_raw)

            # Normalize to be in agrement with the loss
        nabla_params = [nabla_W_e / len(x), nabla_W_x / len(x), nabla_W_h / len(x), nabla_W_y / len(x)]
        return nabla_params

    @staticmethod
    def save(model_path):
        """
        Save model
        """
        pass

    #        par = self.params + self.actvfunc
    #        with open(model_path, 'wb') as fid:
    #            cPickle.dump(par, fid, cPickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(model_path):
        """
        Load model
        """
        pass


# with open(model_path) as fid:
#            par      = cPickle.load(fid, cPickle.HIGHEST_PROTOCOL)
#            params   = par[:len(par)/2]
#            actvfunc = par[len(par)/2:]
#        return params, actvfunc


class RNN:
    def __init__(self, W_e, n_hidd, n_tags, seed=None):
        """
        E       numpy.array Word embeddings of size (n_emb, n_words)
        n_hidd  int         Size of the recurrent layer
        n_tags  int         Total number of tags
        """

        # Dimension of the embeddings
        n_emb = W_e.shape[0]

        # MODEL PARAMETERS
        np.random.seed(seed)
        W_x = np.random.uniform(size=(n_hidd, n_emb))  # Input layer
        W_h = np.random.uniform(size=(n_hidd, n_hidd))  # Recurrent layer
        W_y = np.random.uniform(size=(n_tags, n_hidd))  # Output layer
        # Cast to theano GPU-compatible type
        W_e = W_e.astype(theano.config.floatX)
        W_x = W_x.astype(theano.config.floatX)
        W_h = W_h.astype(theano.config.floatX)
        W_y = W_y.astype(theano.config.floatX)
        # Store as shared parameters
        _W_e = theano.shared(W_e, borrow=True)
        _W_x = theano.shared(W_x, borrow=True)
        _W_h = theano.shared(W_h, borrow=True)
        _W_y = theano.shared(W_y, borrow=True)

        # Class variables
        self.n_hidd = n_hidd
        self.param = [_W_e, _W_x, _W_h, _W_y]

    def _forward(self, _x, _h0=None):
        # Default initial hidden is allways set to zero
        if _h0 is None:
            h0 = np.zeros((1, self.n_hidd)).astype(theano.config.floatX)
            _h0 = theano.shared(h0, borrow=True)

        # COMPUTATION GRAPH

        # Get parameters in nice form
        _W_e, _W_x, _W_h, _W_y = self.param

        # NOTE: Since _x contains the indices rather than full one-hot vectors,
        # use _W_e[:, _x].T instead of T.dot(_x, _W_e.T)

        ###########################
        # Solution to Exercise 6.3 

        # Embedding layer 
        _z1 = _W_e[:, _x].T

        # This defines what to do at each step
        def rnn_step(_x_tm1, _h_tm1, _W_x, W_h):
            return T.nnet.sigmoid(T.dot(_x_tm1, _W_x.T) + T.dot(_h_tm1, W_h.T))

        # This creates the variable length computation graph (unrols the rnn)
        _h, updates = theano.scan(fn=rnn_step,
                                  sequences=_z1,
                                  outputs_info=dict(initial=_h0),
                                  non_sequences=[_W_x, _W_h])

        # Remove intermediate empty dimension
        _z2 = _h[:, 0, :]

        # End of solution to Exercise 6.3
        ###########################

        # Output layer
        _p_y = T.nnet.softmax(T.dot(_z2, _W_y.T))

        return _p_y


class LSTM:
    def __init__(self, W_e, n_hidd, n_tags):

        # Dimension of the embeddings
        n_emb = W_e.shape[0]

        # MODEL PARAMETERS
        W_x = np.random.uniform(size=(4 * n_hidd, n_emb))  # RNN Input layer
        W_h = np.random.uniform(size=(4 * n_hidd, n_hidd))  # RNN recurrent var
        W_c = np.random.uniform(size=(3 * n_hidd, n_hidd))  # Second recurrent var
        W_y = np.random.uniform(size=(n_tags, n_hidd))  # Output layer
        # Cast to theano GPU-compatible type
        W_e = W_e.astype(theano.config.floatX)
        W_x = W_x.astype(theano.config.floatX)
        W_h = W_h.astype(theano.config.floatX)
        W_c = W_c.astype(theano.config.floatX)
        W_y = W_y.astype(theano.config.floatX)
        # Store as shared parameters
        _W_e = theano.shared(W_e, borrow=True)
        _W_x = theano.shared(W_x, borrow=True)
        _W_h = theano.shared(W_h, borrow=True)
        _W_c = theano.shared(W_c, borrow=True)
        _W_y = theano.shared(W_y, borrow=True)

        # Class variables
        self.n_hidd = n_hidd
        self.param = [_W_e, _W_x, _W_h, _W_c, _W_y]

    def _forward(self, _x, _h0=None, _c0=None):

        # Default initial hidden is allways set to zero
        if _h0 is None:
            h0 = np.zeros((1, self.n_hidd)).astype(theano.config.floatX)
            _h0 = theano.shared(h0, borrow=True)
        if _c0 is None:
            c0 = np.zeros((1, self.n_hidd)).astype(theano.config.floatX)
            _c0 = theano.shared(c0, borrow=True)

        # COMPUTATION GRAPH

        # Get parameters in nice form
        _W_e, _W_x, _W_h, _W_c, _W_y = self.param
        H = self.n_hidd

        # Embedding layer 
        _z1 = _W_e[:, _x].T

        # Per loop operation 
        def _step(_x_tm1, _h_tm1, _c_tm1, _W_x, _W_h, _W_c):

            # LINEAR TRANSFORMS
            # Note that all transformations per variable are stacked for
            # efficiency each individual variable is then selected using slices
            # of H size (see below)
            _z_x = T.dot(_x_tm1, _W_x.T)
            _z_h = T.dot(_h_tm1, _W_h.T)
            _z_c = T.dot(_c_tm1, _W_c.T)

            # GATES
            # Note the subtlety: _x_tm1 and hence _z_x are flat and have size
            # (H,) _h_tm1 and _c_tm1 are not and thus have size (1, H)
            _i_t = T.nnet.sigmoid(_z_x[:H] + _z_h[:, :H] + _z_c[:, :H])
            _f_t = T.nnet.sigmoid(_z_x[H:2 * H] + _z_h[:, H:2 * H] + _z_c[:, H:2 * H])
            _o_t = T.nnet.sigmoid(_z_x[3 * H:4 * H] + _z_h[:, 3 * H:4 * H] + _z_c[:, 2 * H:3 * H])

            # HIDDENS
            _c_t = _f_t * _c_tm1 + _i_t * T.tanh(_z_x[2 * H:3 * H] + _z_h[:, 2 * H:3 * H])
            _h_t = _o_t * T.tanh(_c_t)

            return _h_t, _c_t

        # Unrol the loop
        _h, updates = theano.scan(_step,
                                  sequences=_z1,
                                  outputs_info=[_h0, _c0],
                                  non_sequences=[_W_x, _W_h, _W_c])
        # Just keep the first hidden, remove intermediate empty dimension
        _z2 = _h[0][:, 0, :]

        # Output layer
        _p_y = T.nnet.softmax(T.dot(_z2, _W_y.T))

        return _p_y
