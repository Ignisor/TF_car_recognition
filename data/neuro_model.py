from urllib.request import urlopen
from io import BytesIO
from PIL import Image as PIL_Image
import time

import tensorflow as tf
from tensorflow.python.framework.errors_impl import NotFoundError
from numpy import array

from data.dataset import ImageSet, CifarImageSet


class Neuro(object):
    def __init__(self):
        self.x = tf.placeholder(tf.float32, shape=[None, 64 * 64, 3])
        x_image = tf.reshape(self.x, [-1, 64, 64, 3])

        # First layer:
        W_conv1 = self.weight_variable([5, 5, 3, 32])
        b_conv1 = self.bias_variable([32])

        h_conv1 = tf.nn.relu(self.conv2d(x_image, W_conv1) + b_conv1)
        h_pool1 = self.max_pool_2x2(h_conv1)

        # Second layer:
        W_conv2 = self.weight_variable([5, 5, 32, 64])
        b_conv2 = self.bias_variable([64])

        h_conv2 = tf.nn.relu(self.conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = self.max_pool_2x2(h_conv2)

        # Densely connected layer:
        W_fc1 = self.weight_variable([16 * 16 * 64, 1024])
        b_fc1 = self.bias_variable([1024])

        h_pool2_flat = tf.reshape(h_pool2, [-1, 16 * 16 * 64])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

        # Dropout:
        self.keep_prob = tf.placeholder(tf.float32)
        self.h_fc1_drop = tf.nn.dropout(h_fc1, self.keep_prob)

        # Readout layer:
        W_fc2 = self.weight_variable([1024, 2])
        b_fc2 = self.bias_variable([2])

        self.y_conv = tf.matmul(self.h_fc1_drop, W_fc2) + b_fc2

        # correct values
        self.y_ = tf.placeholder(tf.float32, [None, 2])

        self.sess = tf.InteractiveSession()
        self.saver = tf.train.Saver()

        try:
            self.saver.restore(self.sess, "data/saved/model.ckpt")
            print("Loaded model from file")
        except NotFoundError:
            tf.global_variables_initializer().run()

    @staticmethod
    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    @staticmethod
    def bias_variable(shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)

    @staticmethod
    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    @staticmethod
    def max_pool_2x2(x):
        return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    def train(self, steps=1000):
        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=self.y_, logits=self.y_conv))

        train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
        correct_prediction = tf.equal(tf.argmax(self.y_conv, 1), tf.argmax(self.y_, 1))

        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        self.sess.run(tf.global_variables_initializer())

        for i in range(steps):
            print(f"started {i+1} training")

            t = time.time()
            batch = CifarImageSet.get_batch(amount=100)
            print(f"data got in: {time.time() - t:.2f}s")

            t = time.time()
            train_step.run(feed_dict={self.x: batch[0], self.y_: batch[1], self.keep_prob: 0.5})
            print(f"train step took: {time.time() - t:.2f}s")

            if (i + 1) % 100 == 0:
                test_batch = CifarImageSet.get_batch(amount=1000, test=True)
                acc = accuracy.eval(feed_dict={self.x: test_batch[0], self.y_: test_batch[1], self.keep_prob: 1.0})
                print(f"step {i+1}, training accuracy {acc}")
                self.saver.save(self.sess, "data/saved/model.ckpt")

        test_batch = CifarImageSet.get_batch(amount=1000, test=True)
        test_acc = accuracy.eval(feed_dict={self.x: test_batch[0], self.y_: test_batch[1], self.keep_prob: 1.0})
        print(f"Test accuracy {test_acc}")

        self.saver.save(self.sess, "data/saved/model.ckpt")

    def is_car(self, image_url):
        t = time.time()
        file = BytesIO(urlopen(image_url).read())

        image = PIL_Image.open(file)
        image = image.resize((64, 64))

        vector = []
        for pixel in image.getdata():
            vector.append(tuple((color/255 for color in pixel[:3])))

        vector = array(vector).reshape(1, 64 * 64, 3)

        print(f"Image processing took: {time.time() - t:.2f}s")

        t = time.time()
        softmax = tf.nn.softmax(logits=self.y_conv)

        result = self.sess.run(softmax, feed_dict={self.x: vector, self.keep_prob: 1.0})[0]
        print(f"Neural network took: {time.time() - t:.2f}s")
        print(result)

        if result[0] > result[1]:
            print("It's NOT a car")
        else:
            print("It's a car")
