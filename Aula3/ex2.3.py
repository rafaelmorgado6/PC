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


# Definindo parâmetros
initial_value = 5  # Valor inicial
increment = 0.1    # Incremento a cada passo
num_steps = 1000

noise = np.random.normal(0, 5, num_steps) # Gera 1000 valores de ruído, com media=0 e desvio=5
measurements = []  # Lista para armazenar as medições ruidosas

# Gera a lista de medições ruidosas com base em um valor verdadeiro que muda ao longo do tempo
for i in range(num_steps):
    
    # Cálculo do valor verdadeiro para a medição atual que aumenta a cada passo
    true_value = initial_value + increment * i
    
    # Adicionando o ruído à medição
    noisy_measurement = true_value + noise[i]
    
    # Armazenando a medição ruidosa na lista
    measurements.append(noisy_measurement)


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


plt.plot(measurements, label='Medições (com ruído)', alpha=0.5) # alpha[0 1] -> transparência
plt.plot(estimates, label='Estimativas do Filtro de Kalman', color='orange')
plt.axhline(y=initial_value, color='g', linestyle='--', label='Valor Verdadeiro (5)')
plt.title('Filtro de Kalman com Valor Variável')
plt.xlabel('Iteração')
plt.ylabel('Valor')
plt.legend()
plt.show()