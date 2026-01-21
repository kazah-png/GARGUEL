"""
Sistema de IA con Aprendizaje Profundo para GARGUEL v1.1
Copyright (c) 2026 kazah-png

Sistema de Machine Learning que aprende de cada partido para optimizar:
- Tiempos de detección
- Precisión de clicks
- Predicción de duraciones
- Optimización de recursos
"""

import numpy as np
import json
import pickle
from datetime import datetime
from pathlib import Path
from collections import deque
import logging

logger = logging.getLogger(__name__)


class NeuralNetwork:
    """Red neuronal simple para predicción"""
    
    def __init__(self, input_size=10, hidden_size=20, output_size=1):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Inicializar pesos aleatorios
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        
        # Historial para visualización
        self.loss_history = []
        self.accuracy_history = []
        
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def sigmoid_derivative(self, x):
        return x * (1 - x)
    
    def forward(self, X):
        """Forward propagation"""
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.z2  # Regresión lineal para salida
        return self.a2
    
    def backward(self, X, y, output, learning_rate=0.01):
        """Backward propagation"""
        m = X.shape[0]
        
        # Calcular gradientes
        self.dz2 = output - y
        self.dW2 = (1/m) * np.dot(self.a1.T, self.dz2)
        self.db2 = (1/m) * np.sum(self.dz2, axis=0, keepdims=True)
        
        self.dz1 = np.dot(self.dz2, self.W2.T) * self.sigmoid_derivative(self.a1)
        self.dW1 = (1/m) * np.dot(X.T, self.dz1)
        self.db1 = (1/m) * np.sum(self.dz1, axis=0, keepdims=True)
        
        # Actualizar pesos
        self.W1 -= learning_rate * self.dW1
        self.b1 -= learning_rate * self.db1
        self.W2 -= learning_rate * self.dW2
        self.b2 -= learning_rate * self.db2
    
    def train(self, X, y, epochs=100, learning_rate=0.01):
        """Entrenar la red"""
        for epoch in range(epochs):
            # Forward
            output = self.forward(X)
            
            # Calcular loss (MSE)
            loss = np.mean((output - y) ** 2)
            self.loss_history.append(loss)
            
            # Calcular accuracy (porcentaje dentro de ±10%)
            predictions = output.flatten()
            targets = y.flatten()
            accuracy = np.mean(np.abs(predictions - targets) / targets < 0.1) * 100
            self.accuracy_history.append(accuracy)
            
            # Backward
            self.backward(X, y, output, learning_rate)
            
            if epoch % 20 == 0:
                logger.debug(f"Epoch {epoch}: Loss={loss:.4f}, Accuracy={accuracy:.2f}%")
        
        return self.loss_history, self.accuracy_history
    
    def predict(self, X):
        """Hacer predicción"""
        return self.forward(X)


class ReinforcementLearner:
    """Sistema de aprendizaje por refuerzo para optimización de acciones"""
    
    def __init__(self, n_actions=5):
        self.n_actions = n_actions
        self.Q = {}  # Q-table
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.1  # Exploration rate
        
        self.rewards_history = []
        self.actions_history = []
        
    def get_state_key(self, state):
        """Convertir estado a clave"""
        return tuple(np.round(state, 2))
    
    def choose_action(self, state):
        """Elegir acción (epsilon-greedy)"""
        state_key = self.get_state_key(state)
        
        if state_key not in self.Q:
            self.Q[state_key] = np.zeros(self.n_actions)
        
        # Exploración vs explotación
        if np.random.random() < self.epsilon:
            action = np.random.randint(self.n_actions)
        else:
            action = np.argmax(self.Q[state_key])
        
        self.actions_history.append(action)
        return action
    
    def update(self, state, action, reward, next_state):
        """Actualizar Q-value"""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        if next_state_key not in self.Q:
            self.Q[next_state_key] = np.zeros(self.n_actions)
        
        # Q-learning update
        old_value = self.Q[state_key][action]
        next_max = np.max(self.Q[next_state_key])
        
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.Q[state_key][action] = new_value
        
        self.rewards_history.append(reward)
        
        # Decay epsilon (menos exploración con el tiempo)
        self.epsilon = max(0.01, self.epsilon * 0.995)


class AdaptiveLearningSystem:
    """Sistema de aprendizaje adaptativo completo"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # Redes neuronales para diferentes tareas
        self.time_predictor = NeuralNetwork(input_size=8, hidden_size=16, output_size=1)
        self.detection_optimizer = NeuralNetwork(input_size=6, hidden_size=12, output_size=1)
        
        # Sistema de refuerzo para acciones
        self.action_optimizer = ReinforcementLearner(n_actions=5)
        
        # Métricas de aprendizaje
        self.learning_metrics = {
            'total_samples': 0,
            'total_training_sessions': 0,
            'current_accuracy': 0.0,
            'best_accuracy': 0.0,
            'avg_prediction_error': 0.0,
            'learning_rate': 0.01,
            'confidence_level': 0.0
        }
        
        # Historial para gráficos
        self.training_history = {
            'timestamps': [],
            'losses': [],
            'accuracies': [],
            'predictions_vs_actual': [],
            'rewards': []
        }
        
        # Cargar modelos si existen
        self.load_models()
        
        logger.info("🧠 Sistema de IA inicializado")
    
    def prepare_features(self, match_data):
        """Preparar características para el modelo"""
        features = [
            match_data.get('difficulty_encoded', 1),  # 0=Fácil, 1=Normal, 2=Difícil
            match_data.get('pre_time', 0) / 60.0,  # Normalizar
            match_data.get('first_half', 0) / 120.0,
            match_data.get('second_half', 0) / 120.0,
            match_data.get('cpu_usage', 0) / 100.0,
            match_data.get('memory_usage', 0) / 100.0,
            match_data.get('hour_of_day', 12) / 24.0,
            match_data.get('errors_recovered', 0) / 5.0
        ]
        return np.array(features).reshape(1, -1)
    
    def train_on_match(self, match_data):
        """Entrenar con datos de un partido"""
        try:
            # Preparar datos
            X = self.prepare_features(match_data)
            y = np.array([[match_data.get('total_time', 0) / 300.0]])  # Normalizar tiempo total
            
            # Entrenar predictor de tiempo
            loss_history, acc_history = self.time_predictor.train(X, y, epochs=10, learning_rate=0.01)
            
            # Actualizar métricas
            self.learning_metrics['total_samples'] += 1
            self.learning_metrics['total_training_sessions'] += 1
            self.learning_metrics['current_accuracy'] = acc_history[-1] if acc_history else 0
            
            if self.learning_metrics['current_accuracy'] > self.learning_metrics['best_accuracy']:
                self.learning_metrics['best_accuracy'] = self.learning_metrics['current_accuracy']
            
            # Actualizar historial
            self.training_history['timestamps'].append(datetime.now().isoformat())
            self.training_history['losses'].extend(loss_history)
            self.training_history['accuracies'].extend(acc_history)
            
            # Calcular confianza
            self.update_confidence()
            
            logger.info(f"🧠 IA entrenada: Accuracy={self.learning_metrics['current_accuracy']:.2f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Error entrenando IA: {e}")
            return False
    
    def predict_match_time(self, match_data):
        """Predecir tiempo de partido con IA"""
        try:
            X = self.prepare_features(match_data)
            prediction = self.time_predictor.predict(X)
            
            # Desnormalizar
            predicted_time = prediction[0][0] * 300.0
            
            # Calcular intervalo de confianza basado en accuracy
            confidence = self.learning_metrics['confidence_level']
            error_margin = predicted_time * (1 - confidence / 100) * 0.5
            
            return {
                'predicted_time': int(predicted_time),
                'confidence': confidence,
                'min_time': int(predicted_time - error_margin),
                'max_time': int(predicted_time + error_margin),
                'model_accuracy': self.learning_metrics['current_accuracy']
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo: {e}")
            return None
    
    def optimize_detection(self, detection_data):
        """Optimizar parámetros de detección con IA"""
        try:
            features = [
                detection_data.get('template_size', 100) / 500.0,
                detection_data.get('current_threshold', 0.6),
                detection_data.get('avg_confidence', 0.7),
                detection_data.get('detection_time', 0.5),
                detection_data.get('cpu_usage', 50) / 100.0,
                detection_data.get('cache_hit_rate', 0.9)
            ]
            
            X = np.array(features).reshape(1, -1)
            optimal_threshold = self.detection_optimizer.predict(X)
            
            return {
                'optimal_threshold': float(optimal_threshold[0][0]),
                'confidence': self.learning_metrics['confidence_level']
            }
            
        except Exception as e:
            logger.error(f"Error optimizando detección: {e}")
            return None
    
    def learn_from_action(self, state, action, reward, next_state):
        """Aprendizaje por refuerzo de acciones"""
        self.action_optimizer.update(state, action, reward, next_state)
        self.training_history['rewards'].append(reward)
    
    def get_optimal_action(self, state):
        """Obtener acción óptima para un estado"""
        return self.action_optimizer.choose_action(state)
    
    def update_confidence(self):
        """Actualizar nivel de confianza del modelo"""
        if self.learning_metrics['total_samples'] < 10:
            self.learning_metrics['confidence_level'] = 20.0
        elif self.learning_metrics['total_samples'] < 30:
            self.learning_metrics['confidence_level'] = 50.0
        elif self.learning_metrics['total_samples'] < 50:
            self.learning_metrics['confidence_level'] = 70.0
        else:
            # Basado en accuracy
            acc = self.learning_metrics['current_accuracy']
            samples = min(self.learning_metrics['total_samples'], 100)
            self.learning_metrics['confidence_level'] = min(95.0, (acc * 0.7 + samples * 0.3))
    
    def get_learning_visualization_data(self):
        """Obtener datos para visualización del aprendizaje"""
        return {
            'metrics': self.learning_metrics,
            'history': {
                'losses': self.training_history['losses'][-100:],  # Últimos 100
                'accuracies': self.training_history['accuracies'][-100:],
                'rewards': self.training_history['rewards'][-100:]
            },
            'neural_network': {
                'layers': [self.time_predictor.input_size, 
                          self.time_predictor.hidden_size, 
                          self.time_predictor.output_size],
                'total_parameters': (self.time_predictor.W1.size + 
                                   self.time_predictor.W2.size)
            }
        }
    
    def save_models(self):
        """Guardar modelos entrenados"""
        try:
            # Guardar red neuronal
            model_data = {
                'time_predictor': {
                    'W1': self.time_predictor.W1.tolist(),
                    'b1': self.time_predictor.b1.tolist(),
                    'W2': self.time_predictor.W2.tolist(),
                    'b2': self.time_predictor.b2.tolist(),
                    'loss_history': self.time_predictor.loss_history,
                    'accuracy_history': self.time_predictor.accuracy_history
                },
                'detection_optimizer': {
                    'W1': self.detection_optimizer.W1.tolist(),
                    'b1': self.detection_optimizer.b1.tolist(),
                    'W2': self.detection_optimizer.W2.tolist(),
                    'b2': self.detection_optimizer.b2.tolist()
                },
                'action_optimizer_Q': self.action_optimizer.Q,
                'learning_metrics': self.learning_metrics,
                'training_history': self.training_history
            }
            
            with open(self.model_path / 'ai_models.pkl', 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info("💾 Modelos de IA guardados")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
            return False
    
    def load_models(self):
        """Cargar modelos entrenados"""
        try:
            model_file = self.model_path / 'ai_models.pkl'
            if not model_file.exists():
                logger.info("No hay modelos previos, empezando desde cero")
                return False
            
            with open(model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            # Restaurar red neuronal
            self.time_predictor.W1 = np.array(model_data['time_predictor']['W1'])
            self.time_predictor.b1 = np.array(model_data['time_predictor']['b1'])
            self.time_predictor.W2 = np.array(model_data['time_predictor']['W2'])
            self.time_predictor.b2 = np.array(model_data['time_predictor']['b2'])
            self.time_predictor.loss_history = model_data['time_predictor']['loss_history']
            self.time_predictor.accuracy_history = model_data['time_predictor']['accuracy_history']
            
            self.detection_optimizer.W1 = np.array(model_data['detection_optimizer']['W1'])
            self.detection_optimizer.b1 = np.array(model_data['detection_optimizer']['b1'])
            self.detection_optimizer.W2 = np.array(model_data['detection_optimizer']['W2'])
            self.detection_optimizer.b2 = np.array(model_data['detection_optimizer']['b2'])
            
            self.action_optimizer.Q = model_data['action_optimizer_Q']
            self.learning_metrics = model_data['learning_metrics']
            self.training_history = model_data['training_history']
            
            logger.info(f"✅ Modelos cargados: {self.learning_metrics['total_samples']} muestras, "
                       f"{self.learning_metrics['current_accuracy']:.2f}% accuracy")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            return False
    
    def export_learning_report(self, filename='ai_learning_report.json'):
        """Exportar reporte de aprendizaje"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'learning_metrics': self.learning_metrics,
                'training_history': {
                    'total_epochs': len(self.training_history['losses']),
                    'final_loss': self.training_history['losses'][-1] if self.training_history['losses'] else 0,
                    'final_accuracy': self.training_history['accuracies'][-1] if self.training_history['accuracies'] else 0,
                    'average_reward': np.mean(self.training_history['rewards']) if self.training_history['rewards'] else 0
                },
                'model_architecture': {
                    'time_predictor': f"{self.time_predictor.input_size}-{self.time_predictor.hidden_size}-{self.time_predictor.output_size}",
                    'total_parameters': (self.time_predictor.W1.size + self.time_predictor.W2.size)
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Reporte de IA exportado: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exportando reporte: {e}")
            return None


if __name__ == "__main__":
    # Test del sistema
    print("🧠 Testing AI Learning System...")
    
    ai = AdaptiveLearningSystem('test.db')
    
    # Simular entrenamiento
    for i in range(50):
        match_data = {
            'difficulty_encoded': np.random.randint(0, 3),
            'pre_time': np.random.randint(40, 60),
            'first_half': np.random.randint(80, 100),
            'second_half': np.random.randint(80, 100),
            'cpu_usage': np.random.randint(30, 60),
            'memory_usage': np.random.randint(40, 70),
            'hour_of_day': np.random.randint(0, 24),
            'errors_recovered': np.random.randint(0, 3),
            'total_time': np.random.randint(200, 250)
        }
        
        ai.train_on_match(match_data)
    
    # Hacer predicción
    test_data = {
        'difficulty_encoded': 1,
        'pre_time': 50,
        'first_half': 90,
        'second_half': 90,
        'cpu_usage': 45,
        'memory_usage': 55,
        'hour_of_day': 14,
        'errors_recovered': 1
    }
    
    prediction = ai.predict_match_time(test_data)
    print(f"\n✅ Predicción: {prediction}")
    
    # Guardar modelos
    ai.save_models()
    
    # Exportar reporte
    ai.export_learning_report()
    
    print("\n🎉 Test completado!")
