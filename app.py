from flask import Flask, jsonify
import glob
from flask_cors import CORS
import boto3

app = Flask(__name__)
CORS(app)

# The actual credentials used during execution have been omitted.
s3 = boto3.client(
    's3', 
    region_name='xxx',
    aws_access_key_id='xxx',
    aws_secret_access_key='xxx'
)
@app.route("/api/user/<user_id>/details")
def get_followers(user_id):
    try:
        #Fetching the file directly from S3
        response = s3.get_object(Bucket='twitter-user-statistics-varnikaa', Key='output/user_statistics/part-00000-3c0488e3-c121-4653-ae98-d55b28183ca6-c000.csv')
        
        # Reading the file from the S3 stream
        for line in response['Body'].iter_lines():
            
            # boto3 returns bytes, so decoding it to a normal string
            decoded_line = line.decode('utf-8')
            parts = decoded_line.strip().split(",")
            
            
            if parts[0] == user_id:
                return f"{user_id} has {parts[1]} followers\n{user_id} has {parts[2]} followees"
                
        return "User not found", 404
        
    except Exception as e:
        print(f"Error: {e}")
        return "Unable to retrieve statistics from S3.", 500
    

if __name__ == "__main__":
    app.run(debug=True)

    '''User ID: 214328887

214328887 has Number of followers 180

214328887 has Number of followees 214
User ID: 107830991

107830991 has Number of followers 180

107830991 has Number of followees 157
'''