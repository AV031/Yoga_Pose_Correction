import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import numpy as np
from typing import List, Tuple

class YogaPoseLSTM:
    def __init__(self, sequence_length: int = 30, num_features: int = 132, num_classes: int = 10):
        self.sequence_length = sequence_length
        self.num_features = num_features
        self.num_classes = num_classes
        self.model = None
        self.class_names = []
        
    def build_model(self) -> tf.keras.Model:
        """Build LSTM model for pose classification"""
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(self.sequence_length, self.num_features)),
            BatchNormalization(),
            Dropout(0.3),
            
            LSTM(64, return_sequences=True),
            BatchNormalization(),
            Dropout(0.3),
            
            LSTM(32, return_sequences=False),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(32, activation='relu'),
            Dropout(0.2),
            
            Dense(self.num_classes, activation='softmax')
        ])
        
        optimizer = Adam(learning_rate=0.001)
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        self.model = model
        return model
    
    def prepare_sequences(self, landmarks_list: List[np.ndarray], labels: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for training"""
        X, y = [], []
        
        for i in range(len(landmarks_list) - self.sequence_length + 1):
            sequence = landmarks_list[i:i + self.sequence_length]
            if len(sequence) == self.sequence_length:
                X.append(sequence)
                y.append(labels[i + self.sequence_length - 1])
        
        return np.array(X), np.array(y)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 50, batch_size: int = 32) -> tf.keras.callbacks.History:
        """Train the LSTM model"""
        if self.model is None:
            self.build_model()
        
        # Convert labels to categorical
        y_train_cat = tf.keras.utils.to_categorical(y_train, num_classes=self.num_classes)
        
        if X_val is not None and y_val is not None:
            y_val_cat = tf.keras.utils.to_categorical(y_val, num_classes=self.num_classes)
            validation_data = (X_val, y_val_cat)
        else:
            validation_data = None
        
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss' if validation_data else 'loss', 
                         patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss' if validation_data else 'loss', 
                              factor=0.5, patience=5, min_lr=1e-7)
        ]
        
        history = self.model.fit(
            X_train, y_train_cat,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def predict(self, sequence: np.ndarray) -> Tuple[str, float, np.ndarray]:
        """Predict pose from sequence"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Ensure sequence has correct shape
        if len(sequence.shape) == 2:
            sequence = np.expand_dims(sequence, axis=0)
        
        predictions = self.model.predict(sequence, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class_idx]
        
        if self.class_names:
            predicted_class = self.class_names[predicted_class_idx]
        else:
            predicted_class = f"Class_{predicted_class_idx}"
        
        return predicted_class, confidence, predictions[0]
    
    def predict_realtime(self, landmarks_buffer: List[np.ndarray]) -> Tuple[str, float]:
        """Predict pose from real-time buffer"""
        if len(landmarks_buffer) < self.sequence_length:
            return "Waiting for data...", 0.0
        
        # Take the last sequence_length frames
        sequence = np.array(landmarks_buffer[-self.sequence_length:])
        return self.predict(sequence)
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        
        # Save class names
        class_names_path = filepath.replace('.h5', '_classes.txt')
        with open(class_names_path, 'w') as f:
            for name in self.class_names:
                f.write(f"{name}\n")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        self.model = tf.keras.models.load_model(filepath)
        
        # Load class names
        class_names_path = filepath.replace('.h5', '_classes.txt')
        try:
            with open(class_names_path, 'r') as f:
                self.class_names = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.class_names = []
    
    def set_class_names(self, class_names: List[str]):
        """Set the class names for predictions"""
        self.class_names = class_names
        self.num_classes = len(class_names)
        
        # Rebuild model if it exists
        if self.model is not None:
            self.build_model()
    
    def get_model_summary(self):
        """Get model summary"""
        if self.model is None:
            self.build_model()
        return self.model.summary()
