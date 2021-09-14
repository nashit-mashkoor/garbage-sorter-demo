import streamlit as st
import requests
import json
import base64
from timeit import default_timer as timer
import glob
import cv2
import numpy as np

server_address = 'http://139.196.126.220/'

def get_bbox(s):
    return [int(x) for x in s.split(', ')]
def make_prediction(image, test_url):
    st.header('Processed Result')
    try:
        content_type = 'image/jpeg'
        headers = {'content-type': content_type}
        with st.spinner('Processing image ....'):
            encoded_string = base64.b64encode(image)
            start = timer()
            print(encoded_string)
            response = requests.post(test_url, data=encoded_string, headers=headers)
            end = timer()
            result_bytes = np.asarray(image, dtype=np.uint8)
            result_img = cv2.imdecode(result_bytes, cv2.IMREAD_COLOR)
            result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
            result_json = json.loads(response.content.decode('utf8').replace("'", '"'))
            with st.container():
                st.subheader('Results:')
                st.write('**Time Taken**: {:.2f}'.format(end - start))
                if result_json['bin_compartment'] != 'No detection':
                    st.write('**Bin compartment opened**: {}'.format(result_json['bin_compartment']))
                    if result_json['first_roi'] is not None:
                        first_roi = get_bbox(result_json['first_roi'])
                        first_class = result_json['first_class']
                        result_img = cv2.rectangle(result_img, (first_roi[1], first_roi[0]), (first_roi[3], first_roi[2]), (0,255,0), 3)
                        cv2.putText(result_img, 'First class: ' + first_class, (first_roi[1], first_roi[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
                    if result_json['second_roi'] != "None":
                        result_json['second_roi'] = result_json['second_roi'].strip('[]')
                        second_roi = get_bbox(result_json['second_roi'])
                        second_class = result_json['second_class']
                        result_img = cv2.rectangle(result_img, (second_roi[1], second_roi[0]), (second_roi[3], second_roi[2]), (0,255,255), 3)    
                        cv2.putText(result_img, 'Second class: ' + second_class, (second_roi[1], second_roi[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255), 3)

                    st.image((result_img))
                else:
                    st.error('No garbage detected')
    except Exception as e:
        with st.container():
            st.error('Exception : %s' %e)
with st.container():
    st.title('🗑️ Garbage Sorter ')
with st.expander('🆘 Description: '):
    with st.container():
        st.info(f"""  
            1.  Application to verify the **Deployed AI Service** used for garbage sorting
            2.  Possible predicted **Garbage Labels**:  
                1. *Food Waste*  
                2. *Harmful Waste*  
                3. *Other Waste*  
                4. *Recyclable*  
                5. *No detection*  
            3.  Network latency due to China's firewall might increase server's response time deployed on **Ali Baba** if pinged from *Pakistan*
            4.  Current **Server Endpoint**: {server_address}
            """)

with st.expander('🕵️‍♂️ Garbage Detection: '):
    with st.container():
        filename = st.file_uploader('Upload an image to detect garbage')

    with st.container():
        if filename is not None:
            st.subheader('Sample Image')
            st.image(filename)
        else:
            st.error('No image uploaded')
    if st.button('Process'):
        make_prediction(bytearray(filename.read()), server_address)
    