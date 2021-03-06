from __future__ import print_function
import keras
import matplotlib
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import matplotlib.pyplot as plt
from keras.models import model_from_json
import matplotlib.cm as cm
from keras.callbacks import ModelCheckpoint
import numpy as np
from keras.utils import np_utils
import requests
requests.packages.urllib3.disable_warnings()
import ssl

# use Keras to import pre-shuffled MNIST database
# getting X_train, y_train , X_test, y_test
(X_train, y_train), (X_test, y_test) = mnist.load_data()

#dimensions
img_rows, img_cols = 28, 28

if K.image_data_format() == 'channels_first':
    X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
    X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
    input_shape = (1, img_rows, img_cols)
else:
    X_train = X_train.reshape(X_train.shape[0], img_rows, img_cols, 1)
    X_test = X_test.reshape(X_test.shape[0], img_rows, img_cols, 1)
    input_shape = (img_rows, img_cols, 1)

print("The MNIST database has a training set of %d examples." % len(X_train))
print("The MNIST database has a test set of %d examples." % len(X_test))

#visulaizing 6 images
"""
fig = plt.figure(figsize=(20,20))
for i in range(6):
    ax = fig.add_subplot(1, 6, i+1, xticks=[], yticks=[])
    ax.imshow(X_train[i], cmap='gray')
    ax.set_title(str(y_train[i]))
"""
#plt.show()

#visualize a single input
def visualize_input(img, ax):
    ax.imshow(img, cmap='gray')
    width, height = img.shape
    thresh = img.max()/2.5
    for x in range(width):
        for y in range(height):
            ax.annotate(str(round(img[x][y],2)), xy=(y,x),
                        horizontalalignment='center',
                        verticalalignment='center',
                        color='white' if img[x][y]<thresh else 'black')

"""
fig = plt.figure(figsize = (12,12))
ax = fig.add_subplot(111)
visualize_input(X_train[0], ax)"""
#plt.show()

#rescaling
X_train = X_train.astype('float32')/255
X_test = X_test.astype('float32')/255

# first ten training labels
print('Integer-valued labels:')
print(y_train[:10])

# one-hot encoding
y_train = np_utils.to_categorical(y_train, 10)
y_test = np_utils.to_categorical(y_test, 10)

# first ten (one-hot encoded) training labels
print('One-hot labels:')
print(y_train[:10])

# define the model
model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(10, activation='softmax'))

# summarize the model
model.summary()

# compiling the model
model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

# evaluating test data
score = model.evaluate(X_test, y_test, verbose=0)
accuracy = 100*score[1]

# test accuracy
print('Test accuracy: %.4f%%' % accuracy)

# training the model
checkpointer = ModelCheckpoint(filepath='mnist.model.best.hdf5',
                               verbose=1, save_best_only=True)
model.fit(X_train, y_train, batch_size=128, epochs=12,
          validation_split=0.2, callbacks=[checkpointer],
          verbose=1, shuffle=True)

# loading the weights that yielded the best validation accuracy
model.load_weights('mnist.model.best.hdf5')

# evaluate test accuracy
score = model.evaluate(X_test, y_test, verbose=0)
accuracy = 100*score[1]

#test loss
print('Test loss:', score[0])

# print test accuracy
print('Test accuracy: %.4f%%' % accuracy)

model_json = model.to_json()
with open("model.json", "w") as json_file:
  json_file.write(model_json)

model.save_weights("model.h5")

print("Saved model to disk")

