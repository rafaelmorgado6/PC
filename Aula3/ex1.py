
def update(mean1, var1, mean2, var2):
    
    new_mean = (mean1*var2 + mean2*var1)/(var1+var2)
    
    new_var = (var1*var2)/(var1+var2)

    return [new_mean, new_var]


def predict(mean1, var1, mean2, var2):

    new_mean = mean1 + mean2

    new_var = var1 + var2

    return [new_mean, new_var]

mean1, var1 = 10, 4    
mean2, var2 = 12, 2

print(update(mean1, var1, mean2, var2))
print(predict(mean1, var1, mean2, var2))