from urllib.request import urlopen
from io import BytesIO
from PIL import Image as PIL_Image

import tensorflow as tf
from tensorflow.python.framework.errors_impl import NotFoundError
from numpy import array

from data.dataset import ImageSet


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


class Neuro(object):
    def __init__(self):
        self.x = tf.placeholder(tf.float32, shape=[None, 64 * 64])

        self.W = tf.Variable(tf.zeros([64 * 64, 2]))
        self.b = tf.Variable(tf.zeros([2]))

        # model on it's own
        self.y = tf.matmul(self.x, self.W) + self.b

        # correct values
        self.y_ = tf.placeholder(tf.float32, [None, 2])

        self.sess = tf.InteractiveSession()
        self.saver = tf.train.Saver()

        try:
            self.saver.restore(self.sess, "data/saved/model.ckpt")
            print("Loaded model from file")
        except NotFoundError:
            tf.global_variables_initializer().run()

    def train(self, steps=1000):
        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=self.y_, logits=self.y))

        train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

        correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))

        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        # train model
        for i in range(steps):
            print(f'Started {i}/{steps} training')
            batch_xs, batch_ys = ImageSet.get_batch(amount=100)
            self.sess.run(train_step, feed_dict={self.x: batch_xs, self.y_: batch_ys})

            if (i+1)%100 == 0:
                test_xs, test_ys = ImageSet.get_batch(test=True)
                print(self.sess.run(accuracy, feed_dict={self.x: test_xs, self.y_: test_ys}))

        test_xs, test_ys = ImageSet.get_batch(test=True)
        print(self.sess.run(accuracy, feed_dict={self.x: test_xs, self.y_: test_ys}))

        save = input("Save model? (y/n) \n")
        if save.lower() == "y":
            self.saver.save(self.sess, "data/saved/model.ckpt")

    def is_car(self, image_url):
        file = BytesIO(urlopen(image_url).read())

        image = PIL_Image.open(file)
        image = image.resize((64, 64))

        vector = []
        for pixel in image.getdata():
            vector.append(pixel[0] / 255)

        vector = array(vector).reshape(1, 64 * 64)

        softmax = tf.nn.softmax(logits=self.y)

        result = self.sess.run(softmax, feed_dict={self.x: vector})[0]

        print(result)

        if result[0] > result[1]:
            print("It's NOT a car")
        else:
            print("It's a car")
