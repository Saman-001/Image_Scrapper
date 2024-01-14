from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
from pymongo.mongo_client import MongoClient
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import os

application = Flask(__name__)
app = application

#routing to the main page of the website
@app.route('/',methods =["GET"])
@cross_origin()
def homepage():
    return render_template("index.html")
# routing to the result page
@app.route('/review',methods=['POST','GET'])
@cross_origin()
def result_page():
    if request.method == 'POST':
        try:
            # taking the user input from the form of index.html
            query = request.form["content"].replace(" ","")

            #making dir if it is not available in the folder
            save_dir = "Images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # fake user agent to avoid blocking by goggle
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # url to search the image/ user input
            main_url = requests.get(f"https://www.google.com/search?q={query}&sca_esv=598359895&tbm=isch&sxsrf=ACQVn0_Qc4a5iH0RSLN6v155tfayXq8AxA:1705230707105&source=lnms&sa=X&ved=2ahUKEwiMkbq039yDAxWwb2wGHcjPCxsQ_AUoAXoECAIQAw&biw=1536&bih=695&dpr=1.25")

            #beautifying the page content/ html tags/ info
            beautify_page = bs(main_url.content,'html.parser')

            # extracting the img tag from the page source
            html_img_tags = beautify_page.find_all('img')

            #deleting the top img tag because it does not contain the image and it will produce error if we do not delete it
            del html_img_tags[0]
            # making the empty list to store all the images and then push them to the Mongo DB
            image = []
            #traversing the img tag of the html
            for i in html_img_tags:
                #extracted the src tage where the url of the image is stored
                image_url = i['src']
                #getting the image tag
                image_data = requests.get(image_url).content
                # defined dictionary and storing some info of the image_________ AND THIS DICT. WILL BE CREATED FOR EVERY ITERATION
                myDict = {"Index" : i , "Image Data" : image_data}
                # Appending the myDict to the empty list i.e. image[]
                image.append(myDict)

                # Writing the name of the image we are storing in  the databse
                with open(os.path.join(save_dir,f"{query}_{image.index(image_url)}.jpg"),"wb") as f:
                    f.write(image_data)

            # Storing the image data on the mogo DB
            uri = "mongodb+srv://saman323:saman323@cluster0.9i3r4fz.mongodb.net/?"
            client = MongoClient(uri)
            db = client["Image_Scrapper"]
            coll = db["Searched_Images"]
            coll.insert_many(image)

            # returing if all the execution is successfully done
            return "Image is successfully Loaded in the Mongo DB"

        # catching any exception
        except Exception as e:
            # logging if any exception as occurred
            logging.info(e)
            return "Something went wrong"

    else :
        return render_template("index.html")
if __name__  ==  "__main__":
    # defining the host and port number for the execution of the program
    app.run(host='0.0.0.0',port=8000)

