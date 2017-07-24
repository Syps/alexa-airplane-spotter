# Alexa Airplane Spotter ✈️
Check out the blog post here: https://www.nicksypteras.com/projects/teaching-alexa-to-spot-airplanes

### Requirements
- RTL-SDR Dongle and [Dump1090](https://github.com/mutability/dump1090)
- MongoDB
- Node.js


### Set Up For Local Use
1. Run Dump1090

   `path/to/dump1090 --interactive --net`

2. Start MongoDB

   `mongod`

3. Load the data into MongoDB

   `python load_db.py`

4. Add your coordinates to the settings.py file

5. Start the local server

   `node server.js`

6. Test it out! `curl http://localhost:3000` to see the description of nearby airplane activity

### Notes
When building the Alexa skill, you will need to upload the `requests` module to AWS Lambda along with `lambda/lambda_helper.py`. You can do this by installing `requests` into the `lambda/` directory via `pip install requests -t ./lambda`, and then uploading the zipped directory.
