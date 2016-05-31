from __future__ import division

import numpy as np
from builtins import range


class LinearClassifier(object):
    def __init__(self):
        self.trained = False

    def train(self, x, y):
        """
        Returns the weight vector.
        """
        raise NotImplementedError('LinearClassifier.train not implemented')

    @staticmethod
    def get_scores(x, w):
        """
        Computes the dot product between X and w.
        """
        return np.dot(x, w)

    @staticmethod
    def get_label(x, w):
        """
        Computes the label for each data point
        """
        scores = np.dot(x, w)
        return np.argmax(scores, axis=1).transpose()

    def test(self, x, w):
        """
        Classifies the points based on a weight vector.
        """
        if not self.trained:
            raise ValueError("Model not trained. Cannot test")
        x = self.add_intercept_term(x)
        return self.get_label(x, w)

    @staticmethod
    def add_intercept_term(x):
        """
        Adds a column of ones to estimate the intercept term for separation boundary.
        """
        nr_x, nr_f = x.shape
        intercept = np.ones([nr_x, 1])
        x = np.hstack((intercept, x))
        return x

    @staticmethod
    def evaluate(truth, predicted):
        correct = 0.0
        total = 0.0
        for i in range(len(truth)):
            if truth[i] == predicted[i]:
                correct += 1
            total += 1
        return correct / total
