import tensorflow as tf
from tensorflow.keras import layers, models

def build_cnn_lstm_model(sequence_length=16, input_shape=(224,224,3)):
    """Builds a CNN+LSTM model using a pretrained ResNet50 base."""
    cnn_base = tf.keras.applications.ResNet50(
        include_top=False, weights='imagenet', pooling='avg', input_shape=input_shape
    )
    cnn_base.trainable = False

    model = models.Sequential([
        layers.TimeDistributed(cnn_base, input_shape=(sequence_length,) + input_shape),
        layers.LSTM(256, return_sequences=False),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(2, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model
