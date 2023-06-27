import sys
from PIL import Image
from keras.models import load_model
import numpy as np
import streamlit as st

st.title('お好み焼き判別AI')

uploaded_file = st.file_uploader("画像アップロード", type='jpg,png')
image = Image.open(uploaded_file)
img_array = np.array(image)
st.image(img_array,caption = 'アップロード画像',use_column_width = True)

model_path = Streamlit/model.h5

image = image.resize((64,64))
model = load_model(model_path)
np_image = np.array(image)
np_image = np_image / 255
np_image = np_image[np.newaxis, :, :, :]
result = model.predict(np_image)
#print(result)
if result[0][0]>0.6:
  st.subheader("この画像はお好み焼きです。")
else:
  st.subheader("この画像はお好み焼きではありません。")
st.subheader("お好み焼き率は",result[0][0]*100,"％ です。")
