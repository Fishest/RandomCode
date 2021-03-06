import codecs
import os
import collections
from six.moves import cPickle
import numpy as np

class InputLoader():
    def __init__(self, data_dir, batch_size, seq_length, encoding='utf-8'):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.encoding = encoding

        input_file = os.path.join(data_dir, "input.txt")
        vocab_file = os.path.join(data_dir, "vocab.pkl")
        tensor_file = os.path.join(data_dir, "data.npy")

        if not (os.path.exists(vocab_file) and os.path.exists(tensor_file)):
            print("reading text file")
            self.preprocess(input_file, vocab_file, tensor_file)
        else:
            print("loading file")
            self.load_file(vocab_file, tensor_file)

        self.create_batches()
        self.reset_batch_pointer()

    def preprocess(self, input_file, vocab_file, tensor_file):
        with codecs.open(input_file, "r", encoding=self.encoding) as f:
            data = f.read()
        counter = collections.Counter(data)
        count_pairs = sorted(counter.items(), key=lambda x: -x[1])
        self.chars, _ = zip(*count_pairs)
        self.vocab_size = len(self.chars)
        self.vocab = dict(zip(self.chars, range(len(self.chars))))
        with open(vocab_file, 'wb') as output:
            cPickle.dump(self.chars, output)
        self.tensor = np.array(list(map(self.vocab.get, data)))
        np.save(tensor_file, self.tensor)

    def load_file(self, vocab_file, tensor_file):
        with open(vocab_file, 'rb') as f:
            self.chars = cPickle.load(f)
        self.vocab_size = len(self.chars)
        self.vocab = dict(zip(self.chars, range(len(self.chars))))
        self.tensor = np.load(tensor_file)
        self.num_batches = int(self.tensor.size / (self.batch_size * self.seq_length))

    def create_batches(self):
        self.num_batches = int(self.tensor.size / (self.batch_size * self.seq_length))

        self.tensor = self.tensor[:self.num_batches * self.batch_size * self.seq_length]
        # I think the following code should be a better way to generate batches, let's see
        self.tensor_length = len(self.tensor)
        start_index = np.random.rand(self.num_batches, 1)
        self.x_batches = []
        self.y_batches = []
        for index in start_index:
            real_index = int(index * (self.tensor_length - self.seq_length * self.batch_size - 1) )
            self.x_batches.append(np.reshape(self.tensor[real_index: real_index + self.seq_length * self.batch_size], (self.batch_size, self.seq_length)))
            self.y_batches.append(np.reshape(self.tensor[real_index+1 : real_index + self.batch_size * self.seq_length + 1], (self.batch_size, self.seq_length)))

        # print(self.tensor.shape)
        # xdata = self.tensor
        # ydata = np.copy(self.tensor)
        # ydata[:-1] = xdata[1:]
        # ydata[-1] = xdata[0]
        # self.x_batches = np.split(xdata.reshape(self.batch_size, -1), self.num_batches, 1)
        # self.y_batches = np.split(ydata.reshape(self.batch_size, -1), self.num_batches, 1)

    def next_batch(self):
        x, y = self.x_batches[self.pointer], self.y_batches[self.pointer]
        self.pointer += 1
        return x, y

    def reset_batch_pointer(self):
        self.pointer = 0
