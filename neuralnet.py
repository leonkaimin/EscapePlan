
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'  # or '3' to only see errors
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Conv1D, MaxPooling1D, Dropout, Concatenate, Reshape
import tensorflow as tf
from settings import *
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# print(tf.config.list_physical_devices('GPU'))


class MyNeuralNet():
    def __init__(self, modname, n):
        self.modname = modname
        self.model_path = f"{settings['data_root']}/{modname}-{n}.weights.h5"

        # Hyperparameters
        self.dropout_rate = 0.2  # Adjusted dropout rate
        self.learning_rate = 0.0001
        num_input = 1
        wd1_num = 16
        bc1_num = 16
        wc1_num = 16

        # Input Layers
        x0_input = Input(shape=(num_input,))
        x1_input = Input(shape=(num_input,))
        x2_input = Input(shape=(num_input,))
        x3_input = Input(shape=(num_input,))

        # Shared Convolutional Layers (applied to both inputs)
        conv_layer = tf.keras.Sequential([
            Reshape((num_input, 1)),
            Conv1D(bc1_num, wc1_num, activation='relu', padding='same'),
            MaxPooling1D(pool_size=1),
            Dropout(self.dropout_rate)  # Dropout before pooling
        ])

        conv1_x0 = conv_layer(x0_input)
        conv1_x1 = conv_layer(x1_input)
        conv1_x2 = conv_layer(x2_input)
        conv1_x3 = conv_layer(x3_input)

        # LSTM Layers
        merged = Concatenate()([conv1_x0, conv1_x1, conv1_x2])
        lstm = LSTM(64, return_sequences=True)(merged)

        # Dense Layers
        dense = Dense(wd1_num, activation='relu')(lstm)
        output = Dense(1)(dense)  # Regression output

        # Create the Model
        self.model = Model(inputs=[x0_input, x1_input, x2_input, x3_input], outputs=output)

        # Compile the Model
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(
                learning_rate=self.learning_rate),
            loss='mse',  # Mean Squared Error for regression
            metrics=['mae']  # Mean Absolute Error for additional evaluation
        )
        # Load Weights (if available)
        if os.path.exists(self.model_path):
            print(f"{self.model_path} Model Found, Restoring")
            self.model.load_weights(self.model_path)

    # ... other methods (train, test, compute_answer)

    def train(self, Xs, Ys, batch_size=32):
        # ... (input validation)
        # Assuming batch training
        history = self.model.fit(
            [Xs[0], Xs[1], Xs[2], Xs[3]], Ys, epochs=1, batch_size=batch_size)
        # Return loss and MAE
        return history.history['loss'][0], history.history['mae'][0]

    def test(self, Xs, Ys):
        loss, mae = self.model.evaluate([Xs[0], Xs[1], Xs[2], Xs[3]], Ys, verbose=0)
        return loss, mae

    def compute_answer(self, Xs):
        ans = self.model.predict([Xs[0], Xs[1], Xs[2], Xs[3]])
        return ans.flatten()  # Flatten the output to a 1D array

    def save(self, modname, n):
        fname = f"{settings['data_root']}/{modname}-{n}.weights.h5"
        self.model.save_weights(fname)
        print(f"Model saved in file: {fname}")
