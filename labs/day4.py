# Exercises for lab day 4 Parsing.
from builtins import input
import lxmls.parsing.dependency_parser as depp

print("Exercise 4.3.1")

dp = depp.DependencyParser()
dp.read_data("portuguese")

input("Press Enter to go on to the next exercise")

print("Exercise 4.3.2")

dp.train_perceptron(10)
dp.test()

input("Press Enter to go on to the next exercise")

print("Exercise 4.3.3")

dp.features.use_lexical = True
dp.read_data("portuguese")
dp.train_perceptron(10)
dp.test()

dp.features.use_distance = True
dp.read_data("portuguese")
dp.train_perceptron(10)
dp.test()

dp.features.use_contextual = True
dp.read_data("portuguese")
dp.train_perceptron(10)
dp.test()

input("Press Enter to go on to the next exercise")

print("Exercise 4.3.4")

dp.train_crf_sgd(10, 0.01, 0.1)
dp.test()

input("Press Enter to go on to the next exercise")

print("Exercise 4.3.5")

dp.read_data("english")
dp.train_perceptron(10)
dp.test()

input("Press Enter to go on to the next exercise")

print("Exercise 4.3.6")

dp = depp.DependencyParser()
dp.features.use_lexical = True
dp.features.use_distance = True
dp.features.use_contextual = True
dp.read_data("english")
dp.projective = True
dp.train_perceptron(10)
dp.test()
