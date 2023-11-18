from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from typing import List
import openai
import uvicorn
import chromadb
from tinytag import TinyTag
from glob import glob
import os

"""
BACKEND USE

Endpoint for multiple audio file uploads using FastAPI
Use IBM Max to generate audio embeddings (Latent Vectors) of the uploaded files
Use Gladia to transcribe audio file
Use OpenAI Ada to generate text embedding of transcript
Store Latent Vectors in Chromadb
Store Text Embeddings in Chromadb

PUBLIC USE

Endpoint for single file upload using FastAPI
Use IBM MAX to generate a latent vector of the uploaded file
Use Gladia to transcribe audio file
Use OpenAI Ada to generate text embedding of transcript
Run a similarity search for latent vectors and return similar results
Run a similarity search for text embeddings and return similar results
Define a weighted sum formula
Calculate the weighted sum for similar embeddings of the same key using similarity scores
Create a single ranking using the updated similarity score
Recommend top 20 results

    
"""

app = FastAPI()
openai.api_key = " "
vector_db = chromadb.Client()
path = 'C:/Users/USER/Documents/BIG PERSONAL PROJECTS/music recommendation/music files/'
audio_dir = glob(path+"/*.mp3")
audio_length = 5

audio_collection = vector_db.create_collection(name='audio_collection')
lyric_collection = vector_db.create_collection(name='lyric_collection')


def get_information(file):
    tag = TinyTag.get(file)
    tag_image = TinyTag.get(file, image=True)
    music_title = tag.title
    metadata = {
    "Song info": {
        "Album": tag.album,
        "Duration": tag.duration,
        "Artist": tag.artist,
        "Genre": tag.genre,
        "Album Cover": tag_image.get_image()
        }
    }   

    
    return music_title, metadata
                        
                        
    

def get_audio_embedding(audio_dir):
    """
    Extracts audio embeddings from a directory of audio files.

    Parameters:
    - audio_dir (list): List of file paths to audio files.

    Returns:
    - embeddings (list): List of numpy arrays representing audio embeddings.
    - metadata (list): List of metadata associated with each audio file.
    - music_title (list): List of music titles extracted from audio files.
    """

    # Initialize lists to store results
    embeddings = []
    metadata = []
    music_title = []
    i = 0

    for file in audio_dir:
        
        print(f'Getting metadata for {str(i)}')
        
        # Call function to get information (title and metadata) from the audio file
        tit, met = get_information(file)
        
        # Append title and metadata to corresponding lists
        music_title.append(tit)
        metadata.append(met)
        print(f'Metadata gotten successfully for {str(i)}')

        # Print information about sending CURL command
        print('Sending CURL command # '+str(i)+'\n')
        
        # Get the file extension
        file_extension = os.path.splitext(file)[1].lstrip('.')
        
        # Construct and execute CURL command to obtain audio embeddings using a local model
        curl_string = str('curl -F "audio=@'+file+'" -XPOST http://127.0.0.1:5000/model/predict > out_'+str(i)+'.json')
        os.system(curl_string)

        # Open and load the JSON file containing the current audio embedding
        current_embedding = open('out_'+str(i)+'.json', 'r')
        current_embedding = json.load(current_embedding)

        print(f'Current embedding: {current_embedding}')
        
        # Convert the embedding to a numpy array
        test = np.asarray(current_embedding['embedding'])

        # Check if the length of the embedding is greater than or equal to a specified threshold (audio_len)
        if(test.shape[0]>=audio_length):
            test = test[0:audio_length,:]
            test = test.flatten()
            embeddings.append(test)
            print("Embedding complete and saved to numpy array! Removing the json file.. \n")
            
        else:
            print("Audio length < 10 seconds.. skipping this file")

        # Remove the temporary json file
        os.system('rm -f '+'out_'+str(i)+'.json')
        i = i+1

    # Return the final results
    return embeddings, metadata, music_title


        
embeddings, metadata, music_title = get_audio_embedding(audio_dir)

print(metadata)