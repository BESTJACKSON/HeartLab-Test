from tensorflow.python.keras import backend as K
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.layers import Flatten, Dense, Dropout
from tensorflow.python.keras.applications.resnet50 import ResNet50
from tensorflow.python.keras.applications.vgg19 import VGG19
from tensorflow.python.keras.applications.inception_v3 import InceptionV3
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
#dataset path
DATASET_PATH = 'train'
DATATEST_PATH = 'test'

IMAGE_SIZE = (224, 224)

# dataset classification
NUM_CLASSES = 2


BATCH_SIZE = 8

FREEZE_LAYERS = 2

NUM_EPOCHS = 20

WEIGHTS_FINAL = 'model-ResNet50-final.h5'

# Generate more data through data set enhancement.
train_datagen = ImageDataGenerator(rotation_range=40,
                                   width_shift_range=0.2,
                                   height_shift_range=0.2,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   channel_shift_range=10,
                                   horizontal_flip=True,
                                   fill_mode='nearest')
train_batches = train_datagen.flow_from_directory(DATASET_PATH,
                                                  target_size=IMAGE_SIZE,
                                                  interpolation='bicubic',
                                                  class_mode='categorical',
                                                  shuffle=True,
                                                  batch_size=BATCH_SIZE)

valid_datagen = ImageDataGenerator()
valid_batches = valid_datagen.flow_from_directory(DATATEST_PATH,
                                                  target_size=IMAGE_SIZE,
                                                  interpolation='bicubic',
                                                  class_mode='categorical',
                                                  shuffle=False,
                                                  batch_size=BATCH_SIZE)


# Output the index value of each category.
for cls, idx in train_batches.class_indices.items():
    print('Class #{} = {}'.format(idx, cls))

# set up resnet50as a pre-training model.
# fully connected layers
net = ResNet50(include_top=False, weights='imagenet', input_tensor=None,
               input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
x = net.output
x = Flatten()(x)

# increase DropOut layer
x = Dropout(0.5)(x)

# increase Dense layer. Use softmax to generate probability values for each category.
output_layer = Dense(NUM_CLASSES, activation='softmax', name='softmax')(x)

# set up freeze-layer layers
net_final = Model(inputs=net.input, outputs=output_layer)
for layer in net_final.layers[:FREEZE_LAYERS]:
    layer.trainable = False
for layer in net_final.layers[FREEZE_LAYERS:]:
    layer.trainable = True

# use the Adam optimizer，running fine-tuning by lower learning rate
net_final.compile(optimizer=Adam(lr=1e-5),
                  loss='categorical_crossentropy', metrics=['accuracy'])


print(net_final.summary())


hist = net_final.fit_generator(train_batches,
                        steps_per_epoch=train_batches.samples // BATCH_SIZE,
                        validation_data=valid_batches,
                        validation_steps=valid_batches.samples // BATCH_SIZE,
                        epochs=NUM_EPOCHS)

def plot_training(history):
    acc = history.history['acc']
    val_acc = history.history['val_acc']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(len(acc))
    plt.plot(epochs, acc, 'b-')
    plt.plot(epochs, val_acc, 'r')
    plt.title('Training and validation accuracy')
    plt.figure()
    plt.plot(epochs, loss, 'b-')
    plt.plot(epochs, val_loss, 'r-')
    plt.title('Training and validation loss')
    plt.show()
plot_training(hist)

net_final.save(WEIGHTS_FINAL)
