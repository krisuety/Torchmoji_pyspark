from __future__ import print_function, division, unicode_literals
import example_helper
import json
import csv
import argparse

import numpy as np
import emoji

from torchmoji.sentence_tokenizer import SentenceTokenizer
from torchmoji.model_def import torchmoji_emojis
from torchmoji.global_variables import PRETRAINED_PATH, VOCAB_PATH
from pyspark.sql.functions import udf
from pyspark.sql.functions import col
#d = [{'content': 'This is shit'}, {'content': 'I love you'}]
from pyspark.sql.session import SparkSession

SPARK = SparkSession.builder.getOrCreate()
#df = SPARK.createDataFrame(d)
EMOJIS = ":joy: :unamused: :weary: :sob: :heart_eyes: \
:pensive: :ok_hand: :blush: :heart: :smirk: \
:grin: :notes: :flushed: :100: :sleeping: \
:relieved: :relaxed: :raised_hands: :two_hearts: :expressionless: \
:sweat_smile: :pray: :confused: :kissing_heart: :heartbeat: \
:neutral_face: :information_desk_person: :disappointed: :see_no_evil: :tired_face: \
:v: :sunglasses: :rage: :thumbsup: :cry: \
:sleepy: :yum: :triumph: :hand: :mask: \
:clap: :eyes: :gun: :persevere: :smiling_imp: \
:sweat: :broken_heart: :yellow_heart: :musical_note: :speak_no_evil: \
:wink: :skull: :confounded: :smile: :stuck_out_tongue_winking_eye: \
:angry: :no_good: :muscle: :facepunch: :purple_heart: \
:sparkling_heart: :blue_heart: :grimacing: :sparkles:".split(' ')

def top_elements(array, k):
    ind = np.argpartition(array, -k)[-k:]
    return ind[np.argsort(array[ind])][::-1]
 
with open(VOCAB_PATH, 'r') as f:
    vocabulary = json.load(f)

st = SentenceTokenizer(vocabulary, 30)

model = torchmoji_emojis(PRETRAINED_PATH)
def sentence_to_emoji_fun(sentence):
    tokenized, _ ,_   = st.tokenize_sentences([sentence])
    prob = model(tokenized)[0]
    emoji_ids = top_elements(prob, 5)
    emojis = map(lambda x: EMOJIS[x], emoji_ids)
    return emoji.emojize("{}".format(' '.join(emojis)), use_aliases=True)


from pyspark.sql.types import StringType

get_emoji = udf(lambda s: sentence_to_emoji_fun(s), StringType())

import requests

import findspark
findspark.init()
import pyspark

from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

from pyspark.sql.types import *
from pyspark.sql.functions import *

spark.sparkContext.setLogLevel("ERROR")

kafka_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "test").load()
kafka_df_string = kafka_df.select(col("key").cast("STRING").alias("key"),col("value").cast("STRING").alias("value"))
kafka_df_string_2 = kafka_df_string.select(col("value"))

new = kafka_df_string_2.withColumn("emoji", get_emoji(kafka_df_string_2.value))




output = new.writeStream.outputMode("append").format("console").option("truncate", "false").trigger(processingTime="3 seconds").start()

#def send_df_to_dashboard(df, id):
#    tag = [str(t.value) for t in df.select("value").take(10)]
    #url = 'http://localhost:8050/update_data'
    #request_data = {'value' : str(value)} #request_data = {'tag': str(tag), 'tag_count': str(tag_count)}
    #print('update dashboard')
    #response = requests.post(url, data=request_data)

#kafka_df_string_2.writeStream.outputMode("complete").foreachBatch(send_df_to_dashboard).trigger(processingTime="3 seconds").start()

#def send_df_to_dashboard(df, id):
#    tag = [str(t.value) for t in df.select("value").take(10)]
    #url = 'http://localhost:8050/update_data'
    #request_data = {'value' : str(value)} #request_data = {'tag': str(tag), 'tag_count': str(tag_count)}
    #print('update dashboard')
    #response = requests.post(url, data=request_data)

#kafka_df_string_2.writeStream.outputMode("complete").foreachBatch(send_df_to_dashboard).trigger(processingTime="3 seconds").start()

output.awaitTermination()





#result = df.select(get_emoji(col('content'))).collect()
#result = [r['<lambda>(content)'] for r in result]
#print(result)
