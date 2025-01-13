import math, random

## 1

# mean1, var1 -> previous belief
# mean2, var2 -> state from measurement

def update(mean1, var1, mean2, var2):
    new_mean = ((mean1 * math.pow(var2,2)) + (mean2 * math.pow(var1,2)))/(math.pow(var1,2) + math.pow(var2,2))
    new_var = (math.pow(var1,2) * math.pow(var2,2))/(math.pow(var1,2) + math.pow(var2,2))
    return [new_mean, new_var]

def predict(mean1, var1, mean2, var2):
    new_mean = mean1 + mean2
    new_var = math.pow(var1,2) + math.pow(var2,2)
    return [new_mean, new_var]

## 2

initial_value = 0
initial_variance = 5
first_measurement = 3.606
R = 1.1666
Q = 0

def kalman_gain(propagated_variance, R):
    print(propagated_variance)
    print(R)
    return propagated_variance/(propagated_variance + R)

def kalman_estimate_value(previous_state, measurement, propagated_variance, R):
    return previous_state + (kalman_gain(propagated_variance, R) * (measurement - previous_state))

def kalman_estimate_accuracy(propagated_variance, R):
    return (1 - kalman_gain(propagated_variance, R)) * propagated_variance

def kalman_propagated_variance(_estimated_accuracy, Q):
    return _estimated_accuracy + Q

estimated_value = 0
estimated_accuracy = 0

for i in range(0,10):
    if i == 0:
        estimated_value = kalman_estimate_value(initial_value, first_measurement, initial_variance, R)
        estimated_accuracy = kalman_estimate_accuracy(initial_variance, Q)
    else:
        estimated_value = kalman_estimate_value(estimated_value, random.uniform(1,10), estimated_accuracy, R)
        estimated_accuracy = kalman_estimate_accuracy(estimated_accuracy, Q)

    print('Estimated value: ' + str(estimated_value) + ', estimated accuracy: ' + str(estimated_accuracy))
