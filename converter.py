from pydub import AudioSegment 
import os

path = 'C:/Users/USER/Documents/BIG PERSONAL PROJECTS/music recommendation/music files'
new_path = 'C:/Users/USER/Documents/BIG PERSONAL PROJECTS/music recommendation/music files wav/'

# Create the output directory if it doesn't exist
if not os.path.exists(new_path):
    os.makedirs(new_path)

count = 1
for i in os.listdir(path):
    input_file = os.path.join(path, i)

    # Replace extension properly
    output_file, _ = os.path.splitext(input_file)
    output_file = output_file + '.wav'
    output_file = os.path.join(new_path, os.path.basename(output_file))

    # Convert mp3 file to wav file 
    sound = AudioSegment.from_mp3(input_file) 
    sound.export(output_file, format="wav")
    print(f'{count} file converted')
    count+=1