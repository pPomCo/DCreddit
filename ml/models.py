import numpy as np

from sklearn.linear_model import LinearRegression, Lasso
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPRegressor 
from sklearn.svm import SVR 
from sklearn.tree import DecisionTreeRegressor 

from keras.layers import Layer, Input, Masking, Flatten, Concatenate, Add, Multiply, Lambda, Reshape, RepeatVector, Dot
from keras.layers import BatchNormalization, Dropout
from keras.layers import Embedding, Dense, LSTM, GRU, CuDNNGRU, Conv1D
from keras.layers import TimeDistributed, Bidirectional
from keras.layers import LeakyReLU, Softmax
from keras import regularizers
import keras.backend as K
from keras.models import Model, load_model
from keras.optimizers import Adam, SGD, RMSprop
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from keras.utils import multi_gpu_model

import tensorflow as tf


def get_model():
    return MLPRegressor(solver='sgd', learning_rate='adaptive')
    return SVR()


class MultiHead_Attention(Layer):
    def __init__(self, nb_heads=1, **kwargs):
        self.nb_heads = nb_heads
        super(MultiHead_Attention, self).__init__(**kwargs)

    def build(self, input_shape):
        assert isinstance(input_shape, list)

        query_dim = input_shape[0][-1]
        key_dim = input_shape[1][-1]
        value_dim = input_shape[2][-1]

        self.head_dim = int(value_dim / self.nb_heads)

        self.Wq = self.add_weight(
            shape = (self.nb_heads, query_dim, self.head_dim),
            name = '{}_Wq'.format(self.name),
            initializer = 'glorot_uniform',
        )
        self.Wk = self.add_weight(
            shape = (self.nb_heads, key_dim, self.head_dim),
            name = '{}_Wk'.format(self.name),
            initializer = 'glorot_uniform',
        )
        self.Wv = self.add_weight(
            shape = (self.nb_heads, value_dim, self.head_dim),
            name = '{}_Wv'.format(self.name),
            initializer = 'glorot_uniform',
        )

        self.Wo = self.add_weight(
            shape = (self.nb_heads * self.head_dim, value_dim),
            name = '{}_Wo'.format(self.name),
            initializer = 'glorot_uniform',
        )

        self.built = True

    def call(self, x):
        assert isinstance(x, list)
        q, k, v = x

        queries = tf.einsum('bqo,hof->bhqf', q, self.Wq)
        keys = tf.einsum('bko,hof->bhkf', k, self.Wk)
        values = tf.einsum('bvo,hof->bhvf', v, self.Wv)

        dot_product = K.batch_dot(queries, keys, axes=[3,3])
        dot_product = dot_product / np.sqrt(self.head_dim)

        attention = K.batch_dot(K.softmax(dot_product), values, axes=[2,2])
        attention = K.reshape(
            attention, 
            (-1, K.shape(attention)[2], self.nb_heads * self.head_dim)
        )
        attention = K.dot(attention, self.Wo)

        return attention

    def compute_output_shape(self, input_shape):
        assert isinstance(input_shape, list)
        return (None, input_shape[0][1], input_shape[2][-1])


def RNN(input_layers, output_layers, parameters):
    recurrent_layer = GRU

    # date, distinguished, ?
    in_comment_features = input_layers['comment_features']
    in_body_embedding = input_layers['body_embedding']
    in_subreddit_embedding = input_layers['subreddit_embedding']

    inputs = [
        in_comment_features,
        in_body_embedding,
        in_subreddit_embedding,
    ]
    
    # Is masking possible here ?
    #inputs = Masking()(Concatenate()(inputs))

    # Might need to remove a useless dimension after embedding the ids sequence.
    # (if an embedding layer (id->embedding) is used)
    #embedding = embedding(identifier)
    #embedding = Lambda(
    #    lambda x: K.squeeze(x, axis=-2)
    #)(embedding)

    # Repeat the subreddit embeddings as many times as there are
    # elements in the sequence. This is done to not fill the RNN
    # "memory" with the subreddit embedding.
    def repeat_vector(args):
        layer_to_repeat = args[0]
        sequence_layer = args[1]
        return RepeatVector(K.shape(sequence_layer)[-2])(layer_to_repeat)
    repeated_subreddit_embedding = Lambda(
        repeat_vector, 
        output_shape=(None, K.int_shape(in_subreddit_embedding)[-1])
    )([in_subreddit_embedding, in_comment_features])


    initial_input = Concatenate()([
        in_comment_features,
        in_body_embedding,
        repeated_subreddit_embedding,
    ])

    attended_input = MultiHead_Attention(nb_heads=4)(
        [initial_input, initial_input, initial_input]
    )
    attended_input = Dropout(0.25)(attended_input)
    attended_input = Add()([initial_input, attended_input])
    attended_input = BatchNormalization()(attended_input)

    rnn_1 = recurrent_layer(64, return_sequences=True)(attended_input)
    rnn_2 = recurrent_layer(32)(rnn_1)

    ups = Dense(16, activation='relu')(rnn_2)
    ups = Dropout(0.25)(ups)
    ups = Dense(1)(ups)
    ups = output_layers['ups'](ups)

    model = Model(inputs=inputs, outputs=[ups], name="RNN")

    model.compile(
        loss = {'ups': 'mae'},
        #metrics = {'ups': 'mae'},
        optimizer = Adam(lr=0.0001),
    )
    model.summary()

    return model


# This main is only there to test the model during development
# i.e. : are the shapes ok ? does it compile ? can we feed it data ?
def main():
    # Variable sequence length
    sequence_length = None
    batch_size = 100

    features_dimension = 50
    embedding_dimension = 300

    input_shapes = {
        'comment_features': (batch_size, sequence_length, features_dimension),
        'body_embedding': (batch_size, sequence_length, embedding_dimension),
        'subreddit_embedding': (batch_size, embedding_dimension),
    }
    output_shapes = {
        'ups': (batch_size, 1),
    }

    input_layers = {
        name: Input(
            shape=input_shapes[name][1:],
            name=name,
        ) for name in input_shapes
    }
    output_layers = {
        name: Reshape(
            target_shape=output_shapes[name][1:],
            name=name,
        ) for name in output_shapes
    }

    parameters = {}

    model = RNN(input_layers, output_layers, parameters)
    model.summary()

    #from keras.utils import plot_model
    #plot_model(model, to_file='kek.png', show_shapes=True)

    def gen():
        while True:
            sequence_lengths = [5, 7, 9]
            for sequence_length in sequence_lengths:
                dummy_input_data = {
                    'comment_features': np.ones(
                        (batch_size, sequence_length, features_dimension)
                    ),
                    'body_embedding': np.ones(
                        (batch_size, sequence_length, embedding_dimension)
                    ),
                    'subreddit_embedding': np.ones(
                        (batch_size, embedding_dimension)
                    ),
                }
                dummy_output_data = {
                    'ups': np.ones((batch_size, 1)),
                }

                yield dummy_input_data, dummy_output_data


    model.fit_generator(gen(), steps_per_epoch=3, epochs=5)
    

if __name__ == '__main__':
    main()
