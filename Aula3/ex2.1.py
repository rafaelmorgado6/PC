import numpy as np
import matplotlib.pyplot as plt

def kalmanFilter(measure, oldMeasure, oldVar, measureVariance):

    # Ganho de Kalman determina quanto da nova medição deve ser incorporada à estimativa anterior.
    # Um ganho maior significa que a nova medição é considerada mais confiável.
    KalmanGain = oldVar / (oldVar + measureVariance)

    # Atualiza a estimativa do valor com base na medição atual e na estimativa anterior.
    estValue = oldMeasure + KalmanGain * (measure - oldMeasure)
    
    # Atualiza a incerteza da estimativa. A nova covariância é reduzida pelo ganho de Kalman, 
    # refletindo a maior confiança na nova estimativa.
    estCovariance = (1 - KalmanGain) * oldVar

    return [estValue, estCovariance, KalmanGain]

constValue = 5
noise = np.random.normal(0, 5, 1000) # Gera 1000 valores de ruído, com media=0 e desvio=5
measurements = constValue + noise # Medições ruidosas

# Inicialização do filtro de Kalman
initial_measure = 0  # Estimativa inicial do estado (valor que estamos a tentar rastrear)
initial_variance = 1  # incerteza inicial
measurement_variance = 1.1666 # Variância do ruído nas medições

# Listas para armazenar resultados
estimates = []  # Lista para armazenar as estimativas geradas pelo Filtro de Kalman.
variances = []  # Lista para armazenar as covariâncias associadas às estimativas.

# Processamento das medições com o Filtro de Kalman
current_estimate = initial_measure  # Variáveis que armazenam a estimativa 
current_variance = initial_variance # e a variância atuais.

# Itera sobre cada medição nas measurements
for measure in measurements:

    # Chama kalmanFilter para atualizar a estimativa e a variância com base na nova medição.
    current_estimate, current_variance, Kalman_Gain = kalmanFilter(measure, current_estimate, current_variance, measurement_variance)
    estimates.append(current_estimate)
    variances.append(current_variance)


plt.plot(measurements, label='Medições (com ruído)', alpha=0.5)
plt.plot(estimates, label='Estimativas do Filtro de Kalman', color='orange')
plt.axhline(y=constValue, color='g', linestyle='--', label='Valor Verdadeiro (5)')
plt.title('Filtro de Kalman com Valor Constante(5)')
plt.xlabel('Iteração')
plt.ylabel('Valor')
plt.legend()
plt.show()