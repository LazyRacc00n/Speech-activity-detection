import matplotlib.pyplot as plt
import pickle
import os
import tensorflow as tf
import numpy as np
import keras
from sklearn.metrics import balanced_accuracy_score, precision_recall_fscore_support
from keras.models import model_from_json
from  tensorflow.keras import regularizers
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
os
class Network():
    # Implementation of a simple neural network
    FILELENGTH = 10

    def __init__(self, input_shape=17, optimizer='adam', loss='binary_crossentropy', metrics='accuracy'):
        self.trained = False
        self.model = Sequential()
        self.input_shape = input_shape
        self.model_path = os.path.join(str(__file__)[:-Network.FILELENGTH],  "Model\\model.json")
        self.weights_path = os.path.join(str(__file__)[:-Network.FILELENGTH], "Weights\\model.h5")
        self.history_path = os.path.join(str(__file__)[:-Network.FILELENGTH], "History\\historyDict")
        self.checkpoint_path = "Checkpoint/cp.ckpt"
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics

    def createModel(self):
        # Add a Dense layer with 28 neurons, with relu as activation function and input dimension equal to the number of features
        self.model.add(Dense(28, input_shape=(self.input_shape,), activation='relu'))
        # To produce the output Add a Dense layer with 1 neurons, with sigmoid as activation function
        self.model.add(Dense(1, activation='sigmoid'))

    def compileModel(self):
        self.model.compile(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics)

    def createCheckPoint(self):
        es_callback = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)
        checkpoint_dir = os.path.dirname(self.checkpoint_path)
        cp_callback = ModelCheckpoint(self.checkpoint_path, monitor='val_loss', save_weights_only=True, verbose=1)
        return es_callback, cp_callback

    def trainModel(self, X, y, batch_size= 128, epochs= 300):
        es_callback, cp_callback = self.createCheckPoint()
        self.history = self.model.fit(X, y, batch_size=batch_size, epochs=epochs, shuffle=True, validation_split=0.3, callbacks=[es_callback, cp_callback], verbose=0)
        self.trained = True

    def balance_accuracy(self, y_pred, ytest):
        return balanced_accuracy_score(y_pred, ytest)

    def precisionAndRecall(self, y_pred, y_test):
        precision, recall, _, _ =precision_recall_fscore_support(y_test, y_pred)
        return precision, recall

    def testModel(self, Xtest, ytest):
        if not self.trained:
            raise Exception("The network is not trained yet!")
        y_pred = (self.model.predict(Xtest) > 0.5).astype("int32")
        return self.balance_accuracy(y_pred, ytest)

    def getPrecisionRecall(self, Xtest, ytest):
        if not self.trained:
            raise Exception("The network is not trained yet!")
        y_pred = (self.model.predict(Xtest) > 0.5).astype("int32")
        return self.precisionAndRecall(y_pred, ytest)

    def predictLabel(self, data):
        """
        :param data: matrix where each row represents a frame with its own features
        :return: for each frame the label SPEECH/NONSPEECH
        """
        if not self.trained:
            raise Exception("The network is not trained yet!")
        return (self.model.predict(data) > 0.5).astype("int32")

    def saveModel(self):
        model_json = self.model.to_json()
        with open(self.model_path, "w") as json_file:
            json_file.write(model_json)

    def loadModel(self):
        json_file = open(self.model_path, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)

    def saveWeights(self):
        if not self.trained:
            raise Exception("The network is not trained yet!")
        self.model.save_weights(self.weights_path)

    def loadWeights(self):
        self.model.load_weights(self.weights_path)

    def saveNetwork(self):
        self.saveModel()
        self.saveWeights()
        print("Network saved correctely!")

    def loadNetwork(self):
        self.createModel()
        self.loadWeights()
        self.compileModel()
        self.trained = True
        print("Network loaded correctely!")

    def saveHistory(self):
        if not self.trained:
            raise Exception("The network is not trained yet!")
        with open(self.history_path, 'wb') as file_pi:
            pickle.dump(self.history, file_pi)

    def loadHistory(self):
        self.history = pickle.load(open(self.history_path, "rb"))

    def plotHistory(self):
        if self.history == None:
            raise Exception("The network is not trained yet")

        # Plot training & validation accuracy values
        plt.plot(self.history.history['accuracy'])
        plt.plot(self.history.history['val_accuracy'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Val'], loc='upper left')
        plt.grid()
        plt.show()

        # Plot training & validation loss values
        plt.plot(self.history.history['loss'])
        plt.plot(self.history.history['val_loss'])
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Val'], loc='upper left')
        plt.grid()
        plt.show()

