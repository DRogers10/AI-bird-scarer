# -*- coding: utf-8 -*-
"""Bird Classifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qFQ6PL-73T9S6L3i-fQ0Vu1O9NvBzcEB
"""

! pip install tensorflow tensorflow-gpu opencv-python matplotlib

'tensorflow==2.7.0',
'tf-models-official==2.7.0',
'tensorflow_io==0.23.1',

!pip install tensorflow==2.8
!apt install --allow-change-held-packages libcudnn8=8.1.0.77-1+cuda11.2

import os
import tensorflow as tf
import cv2
import imghdr
import zipfile
import matplotlib.pyplot as plt
import numpy as np

! pip install kaggle

! mkdir ~/.kaggle

! cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

! kaggle datasets download gpiosenka/100-bird-species

! mkdir "/content/sorted"
! mkdir "/content/sorted/birds"
! mkdir "/content/sorted/misc"
! mkdir "/content/imgs"
! mkdir "/content/miscellaneous"

with zipfile.ZipFile("/content/drive/MyDrive/images.zip", 'r') as zip_ref:
    zip_ref.extractall("/content/imgs/miscellaneous/fill")

exts = ["jpeg", "jpg", "bmp", "png"]
count = 0
for image_class in os.listdir("/content/imgs"):
  for test_train_valid in os.listdir(os.path.join("/content/imgs", image_class)):
    if image_class == "bird_species" and count >= 3000:
      continue
    for species in os.listdir(os.path.join("/content/imgs", image_class, test_train_valid)):
      for image in os.listdir(os.path.join("/content/imgs", image_class, test_train_valid, species)):
        image_path = os.path.join("/content/imgs", image_class, test_train_valid, species, image)
        try:
          img = cv2.imread(image_path)
          tip = imghdr.what(image_path)
          if tip not in exts:
            os.remove(image_path)
            print("Not in exts")
          else:
            if image_class == "bird_species":
              if count >= 3000:
                continue
              count += 1
              #print("birds")
              os.chdir("/content/sorted/birds")
              cv2.imwrite(f"image{count}.jpg", img)
            elif image_class == "miscellaneous":
              #print("misc")
              os.chdir("/content/sorted/misc")
              cv2.imwrite(image, img)
        except Exception as e:
          print("Issue", e)
          #os.remove(image_path)

import glob
print(len(glob.glob("/content/sorted/*")))

data = tf.keras.utils.image_dataset_from_directory("/content/sorted")

data_iterator = data.as_numpy_iterator()

batch = data_iterator.next()
print(batch[1])
print(plt.imshow(batch[0][0]/255), batch[1][0])
plt.show()
print(plt.imshow(batch[0][1]/255), batch[1][1])
plt.show()
print(plt.imshow(batch[0][2]/255), batch[1][2])
plt.show()
# Bird = 0
# Other = 1

data = data.map(lambda x,y: (x/255, y))
data = data.map(lambda x,y: (x, y))

scaled_iterator = data.as_numpy_iterator()

batch = scaled_iterator.next()

print(len(data))
train_size = int(len(data)*.7)
val_size = int(len(data)*.2) + 1
test_size = int(len(data)*.1) + 1
print(train_size, val_size, test_size, train_size + val_size + test_size)

train = data.take(train_size)
val = data.skip(train_size).take(val_size)
test = data.skip(train_size+val_size).take(test_size)

model1 = tf.keras.models.Sequential()
model1.add(tf.keras.layers.Conv2D(32, (3,3), 1, activation="relu", input_shape=(256,256,3)))
model1.add(tf.keras.layers.MaxPooling2D((2,2)))
model1.add(tf.keras.layers.Conv2D(64, (3,3), 1, activation="relu"))
model1.add(tf.keras.layers.MaxPooling2D((2,2)))
model1.add(tf.keras.layers.Conv2D(32, (3,3), 1, activation="relu"))
model1.add(tf.keras.layers.MaxPooling2D((2,2)))

model1.add(tf.keras.layers.Dropout(0.6))
model1.add(tf.keras.layers.Flatten())
model1.add(tf.keras.layers.Dense(512, activation="relu"))
model1.add(tf.keras.layers.Dense(1, activation="sigmoid"))
print(model1.summary())

model1.compile(optimizer="adam", loss=tf.losses.BinaryCrossentropy(), metrics=["accuracy"])

model1.fit(train, epochs=30, validation_data=val)

os.chdir("/content")
model1.save("Bird_classifier.h5")

# model1 = tf.keras.models.load_model("Bird_classifier.h5")

precision = tf.keras.metrics.Precision()
recall = tf.keras.metrics.Recall()
accuracy = tf.keras.metrics.BinaryAccuracy()
for batch in test.as_numpy_iterator():
  X, y = batch
  yhat = model1.predict(X)
  precision.update_state(y, yhat)
  recall.update_state(y, yhat)
  accuracy.update_state(y, yhat)

print(f"Precision: {precision.result().numpy()}, Recall: {recall.result().numpy()}, Accuracy {accuracy.result().numpy()}")

# img = cv2.imread("/content/image-small.jpg")
# img = np.array(tf.image.resize(img, (256,256))).astype(int)
# plt.imshow(img)
# img = img.reshape((1,256,256,3)) / 255
# print(model1.predict(img))